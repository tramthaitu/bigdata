# BIGDATA_UEH Project Setup Guide

This guide provides step-by-step instructions to set up the BIGDATA_UEH project, which involves cloning a repository, setting up directory structures, running a Docker Compose environment, triggering an Airflow DAG, and interacting with a MongoDB database.

## Prerequisites

Before starting, ensure you have the following installed:

- **Git**: To clone the repository.
- **Docker**: To run the Docker Compose environment.
- **Docker Compose**: To manage multi-container Docker applications.
- **Web Browser**: To access the Airflow web interface.

## Setup Instructions

Follow these steps to set up the project:

 1. **Create a Project Directory**Create a directory named `BIGDATA_UEH` to house the project files.

    ```bash
    mkdir BIGDATA_UEH
    ```

 2. **Clone the Repository**Navigate to the `BIGDATA_UEH` directory and clone the `bigdata` repository from GitHub.

    ```bash
    cd BIGDATA_UEH
    git clone https://github.com/tuankhoi25/bigdata.git
    ```

 3. **Navigate to the Project Directory**Move into the cloned `bigdata` directory.

    ```bash
    cd bigdata/
    ```

 4. **Create Directory Structure**Create the necessary directories for logs, plugins, and data storage.

    ```bash
    mkdir logs/ plugins/ data/
    ```

 5. **Create Database Directories**Navigate to the `data/` directory and create subdirectories for MongoDB and PostgreSQL data persistence.

    ```bash
    cd data/
    mkdir mongodb/ postgres_data/
    ```

 6. **Return to Project Root**Move back to the root of the `bigdata` directory.

    ```bash
    cd ..
    ```

 7. **Start Docker Compose**Run the Docker Compose setup to start the services defined in the `docker-compose.yml` file.

    ```bash
    docker compose up
    ```

    Note: Ensure the `docker-compose.yml` file is present in the `bigdata/` directory. This command will start all services, including MongoDB, Airflow, and any other configured containers.

 8. **Trigger the Airflow DAG**Open a web browser and navigate to the Airflow web interface at:

    ```
    http://localhost:8080/
    ```

    Log in (default credentials are typically `admin:admin` unless specified otherwise in the `docker-compose.yml` file). Locate the DAG named `crypto_info_dag` and manually trigger it by clicking the "Run" or "Trigger DAG" button.

 9. **Access MongoDB Container**Open an interactive bash session inside the MongoDB container.

    ```bash
    docker exec -it mongodb bash
    ```

10. **Connect to MongoDB**Use the `mongosh` command to connect to the MongoDB database `crypto_db` with the provided credentials.

    ```bash
    mongosh "mongodb://mongodb:mongodb@localhost:27017/crypto_db?authSource=admin"
    ```

11. **Query the Database**Inside the `mongosh` shell, count the number of documents in the `crypto_history` collection.

    ```javascript
    db.crypto_history.countDocuments()
    ```

## Notes

- Ensure the `docker-compose.yml` file is correctly configured to set up the MongoDB service with the specified credentials (`mongodb:mongodb`) and exposes port `27017`, as well as the Airflow service on port `8080`.
- The `crypto_db` database and `crypto_history` collection should be pre-populated or created as part of the application logic or the `crypto_info_dag` execution.
- The `crypto_info_dag` DAG should be defined in the Airflow setup within the repository's DAGs folder.
- If you encounter permission issues, ensure you have appropriate access to the directories and Docker services.
- To stop the Docker Compose services, run `docker compose down` in the `bigdata/` directory.

## Troubleshooting

- **MongoDB Connection Issues**: Verify the MongoDB service is running (`docker ps`) and the credentials match those in the `docker-compose.yml` file.
- **Airflow Web Interface Not Accessible**: Ensure the Airflow service is running and port `8080` is not blocked. Check the Docker Compose logs for errors (`docker compose logs`).
- **DAG Not Visible**: Confirm the `crypto_info_dag` is correctly defined in the Airflow DAGs folder and that Airflow has loaded it (may require a short wait after starting Docker Compose).
- **Docker Compose Fails**: Check for errors in the `docker-compose.yml` file or ensure all required images are available.
- **Directory Creation Errors**: Ensure you have write permissions in the parent directory.

For further assistance, refer to the repository's documentation or contact the project maintainer.