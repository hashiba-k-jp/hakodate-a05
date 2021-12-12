# time scheduler

from src.getInfoFromJMA.getInfo import getInfo, Entry
from apscheduler.schedulers.background import BackgroundScheduler

def printhw():
    print('helloworld')

sched = BackgroundScheduler(standalone=True, coalesce=True, daemon=True, timezone="Asia/Tokyo")
sched.add_job(getInfo, 'interval', minutes=1)
# sched.add_job(printhw, 'interval', seconds=3)
sched.start()
