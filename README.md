# wheniworksync
An application to fetch new events from When I Work and import them to Google Calendar

## setup

First, follow python quickstart instructions for Google Calendar API at https://developers.google.com/workspace/calendar/api/quickstart/python

If you do not have a Google Workspace account, you will have to use External for project audience and add your own Google account under the authorized test accounts. 

Clone this repository and keep the .json generated in the root directory here as `credentials.json`.

Then, under Data Access for the Google Cloud project, add the Google Calendar API scope at ./auth/calendar

From When I Work, copy and paste your .ics download link to a file named calendar_key.txt in this directory.

Create and activate your virtual environment

Finally:
```
pip install -r requirements.txt
python main.py
```