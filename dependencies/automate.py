from dependencies import mongo
from dependencies import email
from models.opportunities import Job

subscribers = mongo.db["subscribers"]

async def sendBulkMails(job: Job):
    subscriberList = subscribers.find(
        {}
    )
    for i in subscriberList:
        email.send_opportunity(i["email"], job)