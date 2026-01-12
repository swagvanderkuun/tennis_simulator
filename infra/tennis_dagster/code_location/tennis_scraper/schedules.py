from dagster import DefaultScheduleStatus, ScheduleDefinition

from .jobs import scrape_elo_job


# Daily at 03:15
scrape_elo_daily = ScheduleDefinition(
    job=scrape_elo_job,
    cron_schedule="15 3 * * *",
    default_status=DefaultScheduleStatus.STOPPED,
)

all_schedules = [scrape_elo_daily]


