from gcsa.google_calendar import GoogleCalendar
from gcsa.event import Event
from datetime import datetime, timedelta, time
import requests
import os
import json

r = requests
notion_school_token = os.environ['NOTION_SCHOOL_TOKEN']

database_url = '0f12c7d9f40f47b5addec2201b4edc0a'
new_page_url = "https://api.notion.com/v1/pages"
users_url ="https://api.notion.com/v1/users"

headers = {
    "Authorization": "Bearer " + notion_school_token,
    "Content-Type": "application/json",
    "Notion-Version": "2022-06-28"
}

days = '88fc70d47eacc75454346d2e8ea9a86f5245c4db41991b54a380e95fa4fc03ff@group.calendar.google.com'
classes = '4098b345fb02af1ab17dcdb3115c326bd77eb09c2f381f8d5d102d84168852ed@group.calendar.google.com'
meetings = 'a7a4e0df11691a3bd2e92b5fb8bde8374fe9b6f770aae14fc71dd5197f735df8@group.calendar.google.com'
gc_days = GoogleCalendar(default_calendar=days)
gc_classes = GoogleCalendar(default_calendar=classes)
gc_meetings = GoogleCalendar(default_calendar=meetings)

class_duration = timedelta(minutes=50)

def get_stuff_per_day(calendar, time_min, time_max):
    dict = {}

    for day in gc_days.get_events(time_min=time_min, time_max=time_max):
        for i in range(1,7):
            if day.summary == f"Day {i}":
                list_of_classes = list(calendar.get_events(time_min=day.start, time_max=day.end))
                dict[f"Day {i}"] = list_of_classes
    
    return dict


def get_empty_date_from_days():
    list = []

    for empty_days in gc_days.get_events(time_min=datetime(2024, 8, 23)):
        list.append(empty_days)
          
    return list
    
empty_days = gc_days.get_events(time_min=datetime(2024, 8, 22))

def add_classes_per_day():
    classes_per_day = get_stuff_per_day(gc_classes)
    for dayy in get_empty_date_from_days():
        new_date = dayy
        get_classes = classes_per_day.get(new_date.summary)
        for i in get_classes:
            stripped_start = i.start.time()
            stripped_end = i.end.time()
            new_event = Event(
                summary=i.summary,
                start=datetime.combine(new_date.start, stripped_start),
                end=datetime.combine(new_date.start, stripped_end)
                )
            event_added = gc_classes.add_event(new_event)
            print(f"In {new_date} you added {event_added}.")

def add_events_to_notion(time_min, time_max):
    for i in gc_classes.get_events(time_min=time_min, time_max=time_max):
        data = {
            'parent': { "database_id": database_url},
            'properties': {
                'Name': {
                    "title": [
                    {
                        "text": {
                            "content": i.summary
                        }
                    }
                    ]
                },
                "Date": {
                    "date": {
                        "start": i.start.strftime("%Y-%m-%d %H:%M:%S"),
                        "end": i.end.strftime("%Y-%m-%d %H:%M:%S"),
                        "time_zone": "America/Bogota"
                    }
                }

            }
        }

        dataa = json.dumps(data)           
    
        response = requests.post(new_page_url, headers=headers, data=dataa)

        if response.status_code == 200:
            print("success")
            print(response.json())
        else:
            print("fail")
            print(response.text)

