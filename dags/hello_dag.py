from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime

def print_hello():
    return 'Hello world!'

with DAG(
    dag_id='hello_dag',
    description='Simple tutorial DAG',
    schedule_interval='0 12 * * *',
    start_date=datetime(2017, 3, 20),
    catchup=False
) as dag:
    hello_operator = PythonOperator(
        task_id='hello_task',
        python_callable=print_hello
    )
