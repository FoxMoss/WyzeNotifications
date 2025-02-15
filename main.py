import os
import time
import requests
from wyze_sdk import Client
from wyze_sdk.models.events import EventAlarmType
from dotenv import load_dotenv
from datetime import timedelta, datetime
load_dotenv()

try:
    client = Client()
    response = client.login(
        email=os.getenv('WYZE_EMAIL'),
        password=os.getenv('WYZE_PASSWORD'),
        key_id=os.getenv('KEY_ID'),
        api_key=os.getenv('API_KEY'))

    access_token = response['access_token']
    refresh_token = response['refresh_token']

    read_messages = []
    reset_counter = 0
    while True:
        for event in client.events.list(begin=datetime.now() - timedelta(minutes=10)):
            if (event.alarm_type == EventAlarmType.MOTION or event.alarm_type == EventAlarmType.DOORBELL_RANG) and not (event.id in read_messages):
                print(event.id)
                attach = ""
                if (len(event.files) > 0):
                    attach = event.files[0].url
                requests.post("https://ntfy.sh/" + os.getenv('NTFY_CODE'),
                              data=event.alarm_type.describe() + " event triggered.",
                              headers={
                                  "Title": "Doorbell rang!",
                                  "Priority": "urgent",
                    "Click": "wyze://",
                                  "Tags": "warning",
                                  "Attach": attach
                })
                read_messages.append(event.id)
        reset_counter += 1
        if reset_counter > 10*60:
            read_messages = []
            reset_counter = 0
        time.sleep(1)
except:
    requests.post("https://ntfy.sh/" + os.getenv('NTFY_CODE'),
                  data="Looks your notification system broke, " +
                  "get someone to fix it.",
                  headers={
        "Title": "An error occured.",
        "Priority": "default",
        "Tags": "no_entry",
    })
