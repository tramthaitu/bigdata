from dagster import ScheduleDefinition
from jobs import train_cb_model_job

train_cb_model_schedule = ScheduleDefinition(
    job=train_cb_model_job,
    cron_schedule="0 0 * * 0",
    execution_timezone="Asia/Ho_Chi_Minh",
    description="Lịch trình để chạy job train_model_job hàng tuần."
)