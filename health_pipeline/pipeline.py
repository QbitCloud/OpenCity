from datetime import datetime
from zoneinfo import ZoneInfo

from health_pipeline.scrapper import fetch_page, scrape_centres
from health_pipeline.db import is_connected, save_centres


def run():
    if not is_connected:
        print("Pipeline stopped. MongoDB is not connected.")
        return

    html = fetch_page()
    centres = scrape_centres(html)
    scraped_at = datetime.now(ZoneInfo("Asia/Kolkata")).isoformat(timespec="seconds")
    save_centres(centres, scraped_at)
    print("Health Pipeline Updated")


if __name__ == "__main__":
    run()
