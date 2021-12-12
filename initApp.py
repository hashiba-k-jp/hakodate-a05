# time scheduler

def initApp():
    from src.getInfoFromJMA.getInfo import getInfo, Entry
    from apscheduler.schedulers.background import BackgroundScheduler


    sched = BackgroundScheduler(standalone=True, coalesce=True, daemon=True, timezone="Asia/Tokyo")
    sched.add_job(getInfo, 'interval', minutes=1)
    sched.start()
