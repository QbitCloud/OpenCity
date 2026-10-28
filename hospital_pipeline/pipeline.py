from datetime import datetime
from zoneinfo import ZoneInfo

from hospital_pipeline.scrapper import scrape_hospitals
from hospital_pipeline.db import is_connected, save_hospitals


def run():
    if not is_connected:
        print("Pipeline stopped. MongoDB is not connected.")
        return

    hospitals = scrape_hospitals()
    scraped_at = datetime.now(ZoneInfo("Asia/Kolkata")).isoformat(timespec="seconds")
    save_hospitals(hospitals, scraped_at)
    print("Hospital Pipeline Updated")


if __name__ == "__main__":
    run()
