from dagster import Definitions

from .jobs import all_jobs
from .schedules import all_schedules

defs = Definitions(jobs=all_jobs, schedules=all_schedules)


