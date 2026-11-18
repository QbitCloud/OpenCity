from datetime import datetime
from zoneinfo import ZoneInfo

from school_pipeline.scrapper import scrape_schools
from school_pipeline.db import next_year, save_schools


def run():
    year_id = next_year()
    schools = scrape_schools(year_id)
    scraped_at = datetime.now(ZoneInfo("Asia/Kolkata")).isoformat(timespec="seconds")
    save_schools(schools, scraped_at)
    print("Data Updation Successful")


if __name__ == "__main__":
    run()