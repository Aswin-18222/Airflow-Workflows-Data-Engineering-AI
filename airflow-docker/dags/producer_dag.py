import os
import sys
from airflow import DAG
from airflow.providers.docker.operators.docker import DockerOperator
from datetime import datetime
from docker.types import Mount

default_args = {
    'owner': 'aswin',
    'start_date': datetime(2025, 9, 22),
    'retries': 1,
}

with DAG(
    dag_id='automated_kafka_pipeline',
    default_args=default_args,
    schedule_interval='@daily',
    catchup=False,
    description='Automates Kafka producer and consumer using Docker containers',
) as dag:

    run_producer = DockerOperator(
        task_id='run_kafka_producer',
        image='news-ingestor',
        docker_url='unix://var/run/docker.sock',
        network_mode='airflow-docker_default',
        auto_remove=True
    )

    run_consumer = DockerOperator(
        task_id='run_kafka_consumer',
        image='news-consumer',
        docker_url='unix://var/run/docker.sock',
        network_mode='airflow-docker_default',
        mounts=[
            Mount(
                source='C:/Users/U6075901/OneDrive - Clarivate Analytics/Documents/Python Scripts/Airflow/Airflow-Workflows-Data-Engineering-AI/airflow-docker/data-store',
                target='/app/data-store',
                type='bind'
            )
        ],
        auto_remove=True
    )

    run_producer >> run_consumer

