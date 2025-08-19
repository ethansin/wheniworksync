import schedule
import time

from utils import load_calendar_events, create_events, download_file

def main():

    with open("calendar_key.txt", "r") as f:
        url = f.read().strip()

    filepath = download_file(url)
    events = load_calendar_events(filepath)
    create_events(events)

if __name__ == "__main__":

    print("Starting When I Work Calendar Sync...")
    schedule.every().day.at("00:00").do(main)

    count = 0
    hours = 0
    while True:
        if count % 60 == 0:
            hours += 1
            print(f"Calendar Sync has been running for {hours} hours.")
        schedule.run_pending()
        time.sleep(60)
        count += 1