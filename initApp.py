# time scheduler

from src.getInfoFromJMA.getInfo import getInfo, Entry
from apscheduler.schedulers.blocking import BlockingScheduler

def printhw():
    print('helloworld')

sched = BlockingScheduler(standalone=True,coalesce=True)
sched.add_job(getInfo, 'interval', minutes=1)
sched.start()
print('test')