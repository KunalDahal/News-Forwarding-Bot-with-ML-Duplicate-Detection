import os
import sys
import time
import signal
import logging
import subprocess
from multiprocessing import Process, Semaphore
from pathlib import Path

# Configure logging
LOG_DIR = Path(r"Y:\CODIII\PROJECT\News_Forwarding_bot\logs")
LOG_DIR.mkdir(exist_ok=True, parents=True)

logging.basicConfig(
    filename=LOG_DIR / 'launcher.log',
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger('Launcher')

# Global semaphore with 2 permits (one for each bot)
SEMAPHORE = Semaphore(2)

# Path configuration
PROJECT_ROOT = Path(__file__).parent.absolute()
SCRIPTS_DIR = PROJECT_ROOT / "scripts"

def run_script(script_path):
    """Run a Python script with proper environment configuration"""
    SEMAPHORE.acquire()
    try:
        logger.info(f"🚀 Starting {script_path.name}")
        
        # Create environment with PYTHONPATH set
        env = os.environ.copy()
        env["PYTHONPATH"] = str(PROJECT_ROOT)
        
        # Run script with configured environment
        subprocess.run(
            [sys.executable, str(script_path)],
            env=env,
            check=True
        )
    except subprocess.CalledProcessError as e:
        logger.error(f"❌ Script {script_path.name} failed with exit code {e.returncode}")
    except Exception as e:
        logger.error(f"❌ Unexpected error in {script_path.name}: {str(e)}")
    finally:
        SEMAPHORE.release()
        logger.info(f"🛑 {script_path.name} exited")

def manage_process(script_path):
    backoff = 5
    max_backoff = 300
    
    while True:
        try:
            p = Process(target=run_script, args=(script_path,))
            p.start()
            p.join()
            
            if p.exitcode == 0:
                logger.info(f"🔄 Clean exit for {script_path.name}, restarting immediately")
                backoff = 5
            else:
                logger.warning(f"⚠️  {script_path.name} crashed with exit code {p.exitcode}. Restarting in {backoff}s")
                time.sleep(backoff)
                backoff = min(backoff * 2, max_backoff)
                
        except KeyboardInterrupt:
            logger.info("🛑 Received keyboard interrupt, terminating...")
            p.terminate()
            sys.exit(0)

def signal_handler(sig, frame):
    logger.info("🚨 SIGINT received, shutting down...")
    SEMAPHORE.release()
    sys.exit(0)

if __name__ == '__main__':
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    logger.info("🔛 Starting newsbot ecosystem")
    
    # Define script paths
    main_script = SCRIPTS_DIR / "main.py"
    session_script = SCRIPTS_DIR / "session.py"

    # Start main bot first
    main_process = Process(target=manage_process, args=(main_script,))
    main_process.start()
    
    # Allow time for main.py to initialize (adjust as needed)
    logger.info("⏳ Waiting for main.py to initialize...")
    time.sleep(10)  # Adjust this delay based on your initialization needs
    
    # Start session bot after main.py initialization
    session_process = Process(target=manage_process, args=(session_script,))
    session_process.start()

    processes = [main_process, session_process]

    try:
        for p in processes:
            p.join()
            
    except KeyboardInterrupt:
        logger.info("🔌 Main process interrupted")
        for p in processes:
            p.terminate()
        sys.exit(0)