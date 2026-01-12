from dagster import job

from .ops import scrape_elo_op, scrape_draw_op


@job(name="scrape_elo_job")
def scrape_elo_job():
    scrape_elo_op()

@job(name="scrape_draw_job")
def scrape_draw_job():
    scrape_draw_op()


all_jobs = [scrape_elo_job, scrape_draw_job]


