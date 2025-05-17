from dagster import ScheduleDefinition
from jobs import train_model_job

train_model_schedule = ScheduleDefinition(
    job=train_model_job,
    cron_schedule="0 0 1 * *",
    execution_timezone="Asia/Ho_Chi_Minh",
    description="Lịch trình để chạy job train_model_job hàng ngày."
)