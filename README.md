# Big Data Project

A big data processing project using Docker, PostgreSQL, MongoDB, Dagster, Streamlit, and Apache Spark.

## System Architecture

* **PostgreSQL**: Relational database storage
* **MongoDB**: Non-relational (NoSQL) database storage
* **Dagster**: Orchestrator for data pipelines
* **Apache Spark**: Distributed data processing engine
* **Streamlit**: Main application interface for interacting with the system

![Pipeline](https://github.com/user-attachments/assets/1f35ddc3-e2f6-45e6-8e7a-687b1d29670c)

## How to Run the Project

### 1. Create the project directory

```bash
mkdir Bigdata_project
```

### 2. Navigate into the newly created directory

```bash
cd Bigdata_project/
```

### 3. Clone the repository from GitHub

```bash
git clone https://github.com/tuankhoi25/bigdata.git
```

### 4. Navigate into the project folder

```bash
cd bigdata/
```

### 5. Start the core services

```bash
docker-compose up postgres mongodb user-code dagster-webserver dagster-daemon spark-master spark-worker-1 spark-worker-2
```

### 6. Run jobs in Dagster

Visit [http://localhost:3000](http://localhost:3000) and manually trigger the jobs for demo purposes.

### 7. Launch the main application

```bash
docker-compose up app -d
```

Then go to [http://localhost:8501](http://localhost:8501) to interact with the application interface.

### 8. Stop and remove all containers and volumes

```bash
docker-compose down -v
```

### 9. Delete local data

```bash
rm -rf data/
```