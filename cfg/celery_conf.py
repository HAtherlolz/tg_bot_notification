from celery import Celery
from celery.schedules import crontab

from cfg.config import settings

celery_app = Celery('tasks', broker=settings.REDIS_URL)

celery_app.conf.beat_schedule = {
    'check_msg': {
        'task': 'tasks.msg_tasks.check_msg',
        'schedule': crontab(minute='*/1'),
    },
}

celery_app.conf.include = ["tasks.msg_tasks"]

celery_app.conf.timezone = 'Europe/Kiev'
