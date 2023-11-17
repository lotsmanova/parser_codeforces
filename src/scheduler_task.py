import schedule
import time
from src.main import main


def job():
    main()


schedule.every(1).hours.do(job)

while True:
    schedule.run_pending()
    time.sleep(1)
