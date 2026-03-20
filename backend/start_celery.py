"""
启动 Celery Worker 和 Beat
"""
import subprocess
import sys
import time
from pathlib import Path

def start_worker():
    """启动 Celery Worker"""
    print("Starting Celery Worker...")
    cmd = [
        sys.executable,
        "-m", "celery",
        "-A", "app.tasks.celery_app",
        "worker",
        "--loglevel=info",
        "--concurrency=2"
    ]
    return subprocess.Popen(cmd, cwd=Path(__file__).parent.parent.parent)


def start_beat():
    """启动 Celery Beat（定时任务）"""
    print("Starting Celery Beat...")
    cmd = [
        sys.executable,
        "-m", "celery",
        "-A", "app.tasks.celery_app",
        "beat",
        "--loglevel=info"
    ]
    return subprocess.Popen(cmd, cwd=Path(__file__).parent.parent.parent)


def main():
    print("=" * 50)
    print("AI Creator - Celery Services")
    print("=" * 50)
    
    worker = start_worker()
    time.sleep(2)
    beat = start_beat()
    
    print("\nBoth services started.")
    print("Press Ctrl+C to stop.\n")
    
    try:
        # 等待进程
        worker.wait()
        beat.wait()
    except KeyboardInterrupt:
        print("\nShutting down...")
        worker.terminate()
        beat.terminate()
        worker.wait()
        beat.wait()
        print("All services stopped.")


if __name__ == "__main__":
    main()
