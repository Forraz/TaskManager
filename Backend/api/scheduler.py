from apscheduler.schedulers.background import BackgroundScheduler
from django.conf import settings
from django.contrib.auth.models import User
from django.core.mail import send_mail
from .tasks import send_notification
from .models import TasksModel

scheduler = BackgroundScheduler()


def schedule_task(task):
    scheduler.add_job(send_notification, 'date', run_date=task.date_time, args=[task])


def stop_scheduler():
    scheduler.shutdown()
