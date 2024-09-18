from dependencies import mongo
from dependencies import email
from models.opportunities import Job
from concurrent.futures import ThreadPoolExecutor

subscribers = mongo.db["subscribers"]

async def sendBulkMails(job: Job):
    subscriberList = subscribers.find(
        {}
    )

    with ThreadPoolExecutor(max_workers=200) as executor:
        futures = [executor.submit(email.send_opportunity, i["email"], job) for i in subscriberList]
        for future in futures:
            future.result()