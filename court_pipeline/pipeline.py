from datetime import datetime
from zoneinfo import ZoneInfo

from court_pipeline.scrapper import fetch_page, scrape_courts
from court_pipeline.db import is_connected, save_court_officials, save_courts


def run():
    if not is_connected:
        print("Pipeline stopped. MongoDB is not connected.")
        return

    html = fetch_page()
    courts = scrape_courts(html)
    scraped_at = datetime.now(ZoneInfo("Asia/Kolkata")).isoformat(timespec="seconds")
    save_courts(courts, scraped_at)
    print("Court Pipeline Updated")

    # The posts responsible for the figures, read by the issue page
    save_court_officials()
    print("Court officials updated")


if __name__ == "__main__":
    run()
