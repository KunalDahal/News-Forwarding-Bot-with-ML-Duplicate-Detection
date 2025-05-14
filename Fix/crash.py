import asyncio
import logging
import telegram 

logger = logging.getLogger(__name__)

# Modified restart handler with network error suppression
async def run_with_restart(main_function):
    backoff_time = 5
    max_backoff = 300
    while True:
        try:
            await main_function()
            backoff_time = 5
        except (KeyboardInterrupt, SystemExit):
            logger.info("Graceful shutdown initiated")
            break
        except (telegram.error.NetworkError, telegram.error.TimedOut) as e:
            logger.info(f"🔄 Connection lost. Reconnecting in {backoff_time}s...")  # New status message
            await asyncio.sleep(backoff_time)
            backoff_time = min(backoff_time * 2, max_backoff)
        except Exception as e:
            logger.error(f"Critical error: {str(e)}", exc_info=not isinstance(e, telegram.error.NetworkError))
            logger.info(f"Restarting in {backoff_time} seconds...")
            await asyncio.sleep(backoff_time)
            backoff_time = min(backoff_time * 2, max_backoff)