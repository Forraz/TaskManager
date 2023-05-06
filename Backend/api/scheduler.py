from apscheduler.schedulers.background import BackgroundScheduler
from .tasks import send_notification

scheduler = BackgroundScheduler()


def schedule_task(task):
    scheduler.add_job(send_notification, 'date', run_date=task.date_time, args=[task])


def stop_scheduler():
    scheduler.shutdown()
