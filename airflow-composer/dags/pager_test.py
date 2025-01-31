"""PagerDuty Test DAG."""


from datetime import datetime, timedelta


import pendulum
from airflow.hooks.base import BaseHook
from airflow import DAG
from airflow.operators.dummy_operator import DummyOperator
from airflow.sensors.external_task_sensor import ExternalTaskSensor
from airflow.providers.pagerduty.notifications.pagerduty import send_pagerduty_notification


local_tz = pendulum.timezone("US/Pacific")


default_args = {
   "owner": "airflow",
   "depends_on_past": False,
   "retries": 2,
   "retry_delay": timedelta(minutes=5),
   "email": ["charul1896@gmail.com"],
   "email_on_failure": True,
   "email_on_retry": False,
   "sla": timedelta(minutes=20),
}


sla_miss_callback=[
   send_pagerduty_notification(
       summary="The dag {{ dag.dag_id }} has not completed for 20 minutes",
       severity="critical",
       source="airflow dag_id: {{dag.dag_id}}",
       dedup_key="{{dag.dag_id}}",
       component="airflow",
       integration_key="1234abracadabraintegrationkey",
       pagerduty_events_conn_id=BaseHook.get_connection(conn_id="pagerduty_default"),
   )
]


with DAG(
   "pager_test",
   default_args=default_args,
   schedule_interval="@hourly",
   start_date=datetime(2024, 3, 17, 0, tzinfo=local_tz),
   max_active_runs=1,
   is_paused_upon_creation=True,
   sla_miss_callback=sla_miss_callback,
) as dag:
   dag.doc_md = __doc__


   wait_for_prev_run = ExternalTaskSensor(
       task_id="wait_for_prev_run",
       external_dag_id="pager_test",
       external_task_id="all_tasks",
       allowed_states=["success"],
       execution_delta=timedelta(hours=1),
       mode="reschedule",
   )


   all_tasks = DummyOperator(
       task_id="all_tasks",
   )


 
   wait_for_prev_run >> all_tasks
