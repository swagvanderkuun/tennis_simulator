from dagster import DefaultScheduleStatus, ScheduleDefinition

from .jobs import scrape_elo_job, scrape_injuries_job


# Daily at 03:15
scrape_elo_daily = ScheduleDefinition(
    job=scrape_elo_job,
    cron_schedule="15 3 * * *",
    default_status=DefaultScheduleStatus.STOPPED,
)

# Daily at 04:10 (after Elo scrape by default)
scrape_injuries_daily = ScheduleDefinition(
    job=scrape_injuries_job,
    cron_schedule="10 4 * * *",
    default_status=DefaultScheduleStatus.STOPPED,
)

all_schedules = [scrape_elo_daily, scrape_injuries_daily]


