from dagster import asset, AssetExecutionContext
from pyspark.sql import SparkSession
from pyspark.sql.functions import udf, col
from pyspark.sql.types import StringType
from pyspark.sql import functions as F
from pyspark.ml.feature import StringIndexer
from pyspark.sql.types import IntegerType
from pyspark.ml.evaluation import RegressionEvaluator
from pyspark.ml.recommendation import ALS
from pyspark.sql.functions import explode, col


@asset(
    required_resource_keys={"spark", "mongodb"},
    deps=["add_initial_books_details", "add_initial_books_reviews"]
)
def spark_data_asset(context: AssetExecutionContext) -> None:
    """
    1. Read back the data from MongoDB
    2. Create a Spark DataFrame and perform simple transformations
    3. Log/display results
    """
    spark: SparkSession = context.resources.spark

    df_rating = spark.read \
        .format("mongodb") \
        .option("spark.mongodb.database", "books_db") \
        .option("spark.mongodb.collection", "books_reviews") \
        .load()
    context.log.info("1"*10)
    # Lấy ra 4 cột: user_id, profileName, Title, Review/score
        
    df_book = spark.read \
        .format("mongodb") \
        .option("spark.mongodb.database", "books_db") \
        .option("spark.mongodb.collection", "books_details") \
        .load()
    
    context.log.info("2"*10)
    # Book: book_id, title, categories, authors, publisher, image, description 

    context.log.info("1"*10)
    df_rating = df_rating.filter(df_rating.User_id.isNotNull())


    # Định nghĩa hàm clean_profile_name
    def clean_profile_name(profile):
        if profile is None:
            return None
        profile = str(profile)  # Chuyển thành chuỗi
        if '"' in profile:  # Kiểm tra nếu có dấu "
            parts = profile.split('"')  # Tách chuỗi theo dấu "
            if len(parts[0].strip()) > 0:  # Nếu có ký tự trước dấu "
                return parts[0].strip()  # Giữ lại phần trước dấu "
            else:
                return parts[1].strip()  # Nếu không, giữ lại phần giữa hai dấu "
        return profile.strip()  # Nếu không có dấu ", giữ nguyên chuỗi

    # Đăng ký UDF
    clean_profile_udf = udf(clean_profile_name, StringType())

    # Giả sử df là Spark DataFrame có cột profileName
    # Áp dụng UDF vào cột profileName
    df_rating = df_rating.withColumn("profileName", clean_profile_udf(col("profileName")))

    df_cf = df_rating.join(df_book, on="Title", how="inner") \
                 .select("User_id", "`review/score`", "book_id")
    

    # Đếm số lượng book_id duy nhất mà mỗi User_id đã review
    user_review_counts = df_cf.groupBy("User_id").agg(F.countDistinct("book_id").alias("review_count"))

    # Lọc các user có số review > 1
    users_with_multiple_reviews = user_review_counts.filter(user_review_counts.review_count > 2)

    # Kết nối lại với DataFrame gốc để lọc bỏ các dòng có User_id chỉ review 1 lần
    df_cf = df_cf.join(users_with_multiple_reviews, on="User_id", how="inner")
    

    

    # Ánh xạ User_id và book_id thành số nguyên
    user_indexer = StringIndexer(inputCol="User_id", outputCol="User_id_index")
    book_indexer = StringIndexer(inputCol="book_id", outputCol="book_id_index")

    # Áp dụng ánh xạ
    df_cf = user_indexer.fit(df_cf).transform(df_cf)
    df_cf = book_indexer.fit(df_cf).transform(df_cf)

    df_cf = df_cf.withColumn("review/score", col("review/score").cast(IntegerType()))

    # Chia dữ liệu thành train và test
    train_data, test_data = df_cf.randomSplit([0.8, 0.2], seed=42)

    # Xóa các cột User_id và book_id trong cả train_data và test_data
    train_data = train_data.drop("User_id", "book_id")
    test_data = test_data.drop("User_id", "book_id")

    context.log.info("2"*10)
    als = ALS(
        rank = 10,
        maxIter=10,          # Số lần lặp
        regParam=0.2,        # Tham số regularization
        userCol="User_id_index",    # Cột người dùng
        itemCol="book_id_index",    # Cột sách
        ratingCol="review/score",  # Cột đánh giá
        coldStartStrategy="drop"  # Loại bỏ dữ liệu không hợp lệ
    )

    # Huấn luyện mô hình trên tập train
    model = als.fit(train_data)

    # 5. Đánh giá mô hình trên tập test
    predictions = model.transform(test_data)

    evaluator = RegressionEvaluator(
        metricName="rmse",
        labelCol="review/score",
        predictionCol="prediction"
    )

    rmse = evaluator.evaluate(predictions)
    # Xíu ghi log
    context.log.info("3"*10)

    def get_user_recommendations(model, df_cf, num_items=10):
        # Lấy khuyến nghị từ mô hình
        user_recommendations = model.recommendForAllUsers(num_items)

        # Join trực tiếp với `df_cf` để lấy thông tin gốc User_id và book_id
        recommendations_with_ids = user_recommendations.select(
            col("user_id_index"),
            explode("recommendations").alias("rec")
        ).select(
            col("user_id_index"),
            col("rec.book_id_index"),
            col("rec.rating")
        ) \
        .join(df_cf.select("User_id_index", "User_id").distinct(), on="user_id_index", how="left") \
        .join(df_cf.select("book_id_index", "book_id").distinct(), on="book_id_index", how="left")

        return recommendations_with_ids.select("User_id", "book_id", "rating")
    
    # Gọi hàm lấy gợi ý và sắp xếp theo rating giảm dần và User_id tăng dần
    recommend_df = get_user_recommendations(model, df_cf, num_items=10) \
        .orderBy(["User_id", "rating"], ascending=[True, False])  # rating giảm dần, User_id tăng dần

    context.log.info("4"*10)
    
    output_cf = (recommend_df
        .join(df_rating.select("User_id", "profileName"), on="User_id", how="inner")
        .join(df_book.select("book_id", "image", "Title", "categories", "authors", "description", "publisher"),
            on="book_id", how="inner")
    )

    context.log.info("5"*10)

    output_cf.write \
        .format("mongodb") \
        .option("spark.mongodb.database", "books_db") \
        .option("spark.mongodb.collection", "books_recommend") \
        .mode("overwrite") \
        .save()