import os

from app import create_app
from flask import Flask
from apscheduler.schedulers.background import BackgroundScheduler
from scripts.cluster_users import main as cluster_users

app = create_app()
scheduler = BackgroundScheduler()
scheduler.add_job(cluster_users, 'interval', hours=6)
scheduler.start()

if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 5000)),
        debug=False
    )
    