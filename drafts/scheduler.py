import schedule
import time

config = {"frequency": "daily"}

def upload_content(account):
    # Call the account's upload method with content
    print(f"Uploading content to {account}")

def configure_scheduler():
    if config["frequency"] == "daily":
        schedule.every().day.at("09:00").do(upload_content, account="account1")
    elif config["frequency"] == "twice_daily":
        schedule.every().day.at("09:00").do(upload_content, account="account1")
        schedule.every().day.at("15:00").do(upload_content, account="account1")
    elif config["frequency"] == "three_times_daily":
        schedule.every().day.at("09:00").do(upload_content, account="account1")
        schedule.every().day.at("13:00").do(upload_content, account="account1")
        schedule.every().day.at("18:00").do(upload_content, account="account1")

def run_scheduler():
    while True:
        schedule.run_pending()
        time.sleep(1)
        print(1)

configure_scheduler()
run_scheduler()
