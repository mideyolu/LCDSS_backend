from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import delete
from models import Log

async def delete_old_logs(db: AsyncSession):
    try:
        time_threshold = datetime.utcnow() - timedelta(hours=1)
        print(f"Deleting logs older than: {time_threshold}")

        stmt = delete(Log).where(Log.created_at < time_threshold)
        #print(f"Delete statement: {stmt}")

        result = await db.execute(stmt)
        await db.commit()

        #print(f"Deleted {result.rowcount} old logs.")
        return result.rowcount

    except Exception as e:
        print(f"Error deleting old logs: {e}")
        await db.rollback()
        return 0
