from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from app.core.config import get_settings
from app.services.expiry_service import log_today_expiring_policies
from app.core.logging import get_logger

_scheduler = None
log = get_logger()

def start_expiry_scheduler():
    global _scheduler
    settings = get_settings()
    if not settings.SCHEDULER_ENABLED or _scheduler:
        return
    # Remove invalid timezone="local"
    _scheduler = BackgroundScheduler()
    interval = settings.EXPIRY_JOB_INTERVAL_MINUTES
    _scheduler.add_job(
        log_today_expiring_policies,
        trigger=IntervalTrigger(minutes=interval),
        id="policy_expiry_job",
        max_instances=1,
        coalesce=True,
        replace_existing=True,
        misfire_grace_time=120
    )
    _scheduler.start()
    log.info("scheduler.started", interval_minutes=interval)

def shutdown_expiry_scheduler():
    global _scheduler
    if _scheduler:
        _scheduler.shutdown(wait=False)
        log.info("scheduler.stopped", job="policy_expiry_job")
        _scheduler = None