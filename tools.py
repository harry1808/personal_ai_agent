from langchain_core.tools import tool
from langchain_community.tools import DuckDuckGoSearchRun
from datetime import datetime, timedelta
from apscheduler.schedulers.background import BackgroundScheduler
from calendar_tool import create_event
import re

# Start scheduler
scheduler = BackgroundScheduler()
scheduler.start()

reminders = []
meetings = []

# 🔔 Reminder action
def reminder_action(text):
    print(f"\n🔔 REMINDER: {text}\n")


# ⏰ Extract time from text
def extract_time(text):
    match = re.search(r'(\d{1,2})\s*(AM|PM|am|pm)', text)
    if match:
        hour = int(match.group(1))
        period = match.group(2).lower()

        if period == "pm" and hour != 12:
            hour += 12
        if period == "am" and hour == 12:
            hour = 0

        now = datetime.now()
        run_time = now.replace(hour=hour, minute=0, second=0, microsecond=0)

        if run_time < now:
            run_time += timedelta(days=1)

        return run_time

    return datetime.now() + timedelta(minutes=1)


# 🧮 Calculator
@tool
def calculator(query: str) -> str:
    """Use for math calculations"""
    try:
        return str(eval(query))
    except:
        return "Invalid calculation"


# ⏰ Reminder
@tool
def set_reminder(text: str) -> str:
    """Set one reminder only"""

    run_time = extract_time(text)

    scheduler.add_job(
        reminder_action,
        'date',
        run_date=run_time,
        args=[text]
    )

    reminders.append({"text": text, "time": str(run_time)})

    return f"Reminder set for {run_time.strftime('%Y-%m-%d %H:%M')}"


# 📅 Meeting
@tool
def schedule_meeting(text: str) -> str:
    """Schedule meeting in Google Calendar"""
    try:
        from datetime import datetime, timedelta

        now = datetime.now()
        start_time = now.replace(minute=0, second=0) + timedelta(hours=1)

        result = create_event(text, start_time)
        return result

    except Exception as e:
        import traceback
        return f"Error: {str(e)}\n{traceback.format_exc()}"

# 🔎 Search
search = DuckDuckGoSearchRun()

@tool
def search_tool(query: str) -> str:
    """Search internet"""
    return search.run(query)


def get_tools():
    return [calculator, set_reminder, schedule_meeting, search_tool]