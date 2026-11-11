from datetime import datetime
from zoneinfo import ZoneInfo

from officials_pipeline.db import is_connected, save_officials
from officials_pipeline.scrapper import fetch_page, scrape_officials


# Fetch officials and save them in MongoDB.
def run():
    if not is_connected:
        print("Pipeline stopped. MongoDB is not connected.")
        return

    html = fetch_page()
    officials = scrape_officials(html)
    scraped_at = datetime.now(ZoneInfo("Asia/Kolkata")).isoformat(timespec="seconds")

    save_officials(officials, scraped_at)
    print(f"SMC officials updated: {len(officials)} records")


if __name__ == "__main__":
    run()
