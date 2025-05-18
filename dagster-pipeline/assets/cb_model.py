from dagster import asset, AssetExecutionContext
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, row_number, regexp_replace, concat_ws, lower, trim
from pyspark.ml.feature import BucketedRandomProjectionLSH, Normalizer
from pyspark.sql.window import Window
from pyspark.ml.feature import HashingTF, IDF
from pyspark.ml.feature import Tokenizer

@asset(
    required_resource_keys={"spark", "mongodb"},
    deps=["add_initial_books_details"]
)
def cb_model(context: AssetExecutionContext) -> None:
    """
    1. Read back the data from MongoDB
    2. Create a Spark DataFrame and perform simple transformations
    3. Log/display results
    """
    spark: SparkSession = context.resources.spark
    
    df_book = (
        spark.read.format("mongodb")
            .option("spark.mongodb.database", "books_db")
            .option("spark.mongodb.collection", "books_details")
            .load()
            .select("book_id", "Title", "description", "categories", "authors", "publisher", "image")
            .cache()
    )

    context.log.info("loaded data from mongodb")

    df_book = df_book.withColumn("categories", regexp_replace(col("categories"), "[\\[\\]'\"']", ""))

    df_book = df_book.withColumn("authors", regexp_replace(col("authors"), r"[\[\]\"']", ""))


    df_book = df_book.withColumn("attributes", concat_ws(" ", col("categories"), col("authors"), col("publisher"), col("description")))


    df_book = df_book.withColumn("attributes", trim(regexp_replace(lower(df_book["attributes"]), "[^\w\s]", "")))
    
    context.log.info("Data preprocessing completed")

    tokenizer = Tokenizer(inputCol="attributes", outputCol="attributes_tokens")
    df_book = tokenizer.transform(df_book)
    df_book.select("attributes_tokens").show(5, truncate=False)

    context.log.info("Tokenization completed")    

    # TF step
    hashingTF = HashingTF(inputCol="attributes_tokens", outputCol="hash_features", numFeatures=10000)
    df_book = hashingTF.transform(df_book)

    # IDF step
    idf = IDF(inputCol="hash_features", outputCol="features")
    idf_model = idf.fit(df_book)
    df_book = idf_model.transform(df_book)

    context.log.info("TF-IDF transformation completed")

    # Giả sử df_book là DataFrame ban đầu của bạn, đã có cột "features"
    # Bước 1: chuẩn hoá và hash
    normalizer = Normalizer(inputCol="features", outputCol="norm_features", p=2.0)
    df_book_hashed = normalizer.transform(df_book).filter(col("norm_features").isNotNull())

    lsh = BucketedRandomProjectionLSH(
        inputCol="norm_features",
        outputCol="hashes",
        bucketLength=0.5,
        numHashTables=15
    )
    lsh_model = lsh.fit(df_book_hashed)
    df_book_hashed = lsh_model.transform(df_book_hashed).cache()

    # Bước 2: approximate join toàn bộ với chính nó
    df_similar_all = lsh_model.approxSimilarityJoin(
        df_book_hashed, 
        df_book_hashed, 
        threshold=50.0, 
        distCol="euclideanDistance"
    )

    # Bước 3: loại bỏ self match
    df_similar_filtered = df_similar_all \
        .filter(col("datasetA.book_id") != col("datasetB.book_id"))

    # Bước 4: rank và chọn top 10 cho mỗi query book
    windowSpec = Window.partitionBy("datasetA.book_id") \
                    .orderBy("euclideanDistance")

    df_ranked = df_similar_filtered \
        .withColumn("rank", row_number().over(windowSpec)) \
        .filter(col("rank") <= 10)

    context.log.info("Approximate similarity join completed")

    # Bước 5: select cột cuối cùng
    output_cb = df_ranked.select(
        col("datasetA.book_id").alias("query_id"),
        col("datasetB.book_id").alias("book_id"),
        col("datasetB.Title"),
        col("datasetB.categories"),
        col("datasetB.authors"),
        col("datasetB.publisher"),
        col("datasetB.image"),
        col("datasetB.description"),
        col("euclideanDistance")
    )

    context.log.info("Content-based model training completed")
    
    output_cb.write \
        .format("jdbc") \
        .option("url", "jdbc:postgresql://postgres:5432/postgres_db") \
        .option("driver", "org.postgresql.Driver") \
        .option("dbtable", "public.output_cb") \
        .option("user", "postgres_user") \
        .option("password", "postgres_password") \
        .mode("append") \
        .save()

