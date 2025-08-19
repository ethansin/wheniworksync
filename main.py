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
    schedule.every().day.at("00:00").do(main)

    while True:
        schedule.run_pending()
        time.sleep(60)