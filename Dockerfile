FROM apache/airflow:2.10.5-python3.12

# Use the root user to install dependencies and set permissions
USER root

# Copy the application into the container and set permissions
COPY ./requirements.txt /opt/airflow/requirements.txt
COPY ./.env /opt/airflow/.env
COPY ./src/ /opt/airflow/src/

# Set permissions for the airflow user
RUN chown -R 50000:50000 /opt/airflow

# Set PYTHONPATH to include /opt/airflow
ENV PYTHONPATH=/opt/airflow

# Switch to airflow user for application setup
USER airflow

# Install the application dependencies
WORKDIR /opt/airflow
RUN pip install --no-cache-dir -r requirements.txt

# Expose the application port
EXPOSE 8080