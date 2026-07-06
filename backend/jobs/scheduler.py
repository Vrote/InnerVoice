# backend/jobs/scheduler.py
import datetime
import logging
import asyncio
from apscheduler.schedulers.background import BackgroundScheduler
from sqlalchemy.future import select
from backend.database.connection import AsyncSessionLocal
from backend.database.models import User, Message

logger = logging.getLogger(__name__)
scheduler = BackgroundScheduler()


def run_async(coro):
    """Run an async coroutine in a new event loop (for background threads)."""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()


# ── Job 1: Weekly Summary (every Sunday at 9PM UTC) ──────────────────────────
async def generate_all_weekly_summaries():
    logger.info("Scheduler: running generate_all_weekly_summaries")
    from backend.routes.weekly import generate_weekly_summary_data
    async with AsyncSessionLocal() as session:
        res   = await session.execute(select(User))
        users = res.scalars().all()
        for u in users:
            try:
                # Only generate if user had 3+ messages in the last 7 days
                week_start = datetime.datetime.utcnow() - datetime.timedelta(days=7)
                q_cnt = select(Message).where(
                    Message.user_id    == u.id,
                    Message.created_at >= week_start
                )
                cnt_res  = await session.execute(q_cnt)
                msg_count = len(cnt_res.scalars().all())
                if msg_count >= 3:
                    await generate_weekly_summary_data(u.id, session)
            except Exception as e:
                logger.error(f"Weekly summary job failed for user {u.id}: {e}")


# ── Job 2: Monthly Mirror Me Report (1st of month at 10AM UTC) ───────────────
async def generate_all_monthly_reports():
    logger.info("Scheduler: running generate_all_monthly_reports")
    from backend.services.mirror_me_service import get_or_generate_mirror_me_report
    # Prior month
    now   = datetime.datetime.utcnow()
    if now.month == 1:
        month, year = 12, now.year - 1
    else:
        month, year = now.month - 1, now.year

    async with AsyncSessionLocal() as session:
        res   = await session.execute(select(User))
        users = res.scalars().all()
        for u in users:
            try:
                # Only generate if user had 5+ messages last month
                start = datetime.datetime(year, month, 1)
                end   = datetime.datetime(year + 1, 1, 1) if month == 12 else datetime.datetime(year, month + 1, 1)
                q_cnt = select(Message).where(
                    Message.user_id    == u.id,
                    Message.created_at >= start,
                    Message.created_at <  end
                )
                cnt_res  = await session.execute(q_cnt)
                msg_count = len(cnt_res.scalars().all())
                if msg_count >= 5:
                    await get_or_generate_mirror_me_report(u.id, month, year, session)
            except Exception as e:
                logger.error(f"Mirror Me job failed for user {u.id}: {e}")


# ── Job 3: Daily Streak Update (midnight UTC) ─────────────────────────────────
async def update_all_streaks():
    logger.info("Scheduler: running update_all_streaks")
    async with AsyncSessionLocal() as session:
        now = datetime.datetime.utcnow()
        res = await session.execute(select(User))
        users = res.scalars().all()
        for u in users:
            try:
                if u.last_active:
                    delta = now - u.last_active
                    if delta.days > 1:
                        u.streak_count = 0
                        logger.info(f"Streak reset for user {u.id}")
            except Exception as e:
                logger.error(f"Streak update failed for user {u.id}: {e}")
        await session.commit()


def start_scheduler():
    # Every Sunday at 9PM UTC
    scheduler.add_job(
        lambda: run_async(generate_all_weekly_summaries()),
        "cron", day_of_week="sun", hour=21, minute=0
    )
    # 1st of every month at 10AM UTC
    scheduler.add_job(
        lambda: run_async(generate_all_monthly_reports()),
        "cron", day=1, hour=10, minute=0
    )
    # Daily at midnight UTC
    scheduler.add_job(
        lambda: run_async(update_all_streaks()),
        "cron", hour=0, minute=0
    )

    scheduler.start()
    logger.info("APScheduler started: weekly summary, monthly mirror-me, daily streak jobs registered.")
