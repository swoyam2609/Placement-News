from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from dependencies import mongo
from dependencies import email as emailsender
from dependencies import automate
from models.subscribers import Subscriber
from models.opportunities import Job
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
import asyncio

app = FastAPI()

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

subscribers = mongo.db["subscribers"]
jobs = mongo.db["jobs"]
users = mongo.db["pendingusers"]

# Define the ThreadPoolExecutor globally
executor = ThreadPoolExecutor(max_workers=1)

# Mockup for `automate.sendBulkMails(job)`
async def send_bulk_mails(job):
    await automate.sendBulkMails(job)

# Function to run the async task in a background thread
def run_background_task(job):
    loop = asyncio.get_event_loop()  # Get the current event loop
    loop.run_in_executor(executor, asyncio.run, send_bulk_mails(job))

@app.get("/")
async def read_root():
    subscriberList = subscribers.find({})
    jobList = jobs.find({})
    return JSONResponse(
        content={
            "subscribers": len(list(subscriberList)),
            "jobs": len(list(jobList)),
            "author":"Swoyam Siddharth Nayak"
        }
    )

@app.post("/subscribe-newsletter")
async def subscribe_newsletter(user: Subscriber):
    try:
        email = subscribers.find_one({"email":user.email})
        if email:
            return JSONResponse(content={"message": "You are already subscribed"}, status_code=400)
        else:
            subscribers.insert_one(
                {
                    "email": user.email,
                    "name": user.name
                }
            )
            return JSONResponse(content={"message": "Congratulations! you have subscribed"}, status_code=200)
    except Exception as e:
        return JSONResponse(content={"message": f"Failed to subscribe: {e}"}, status_code=404)
    
    
@app.post("/post-job")
async def post_job(job: Job):
    try:
        emailsender.send_otp(job.contributorEmail)
        return JSONResponse(content={"message": "OTP sent for verification"}, status_code=200)
    except Exception as e:
        return JSONResponse(content={"message":f"failed to post job: {e}"}, status_code=404)
    
@app.post("/post-job/verify")
async def verify_job(job: Job, otp: int):
    try:
        user = users.find_one({"email":job.contributorEmail})
        if not user:
            return JSONResponse(content={"message": "User not found"}, status_code=404)
        elif user["otp"] != str(otp):
            return JSONResponse(content={"message": "Invalid OTP"}, status_code=400)
        now = datetime.now()
        job.date = now.strftime("%H:%M %d:%m:%Y")
        jobs.insert_one(
            {
                "company": job.companyName,
                "role": job.role,
                "link":job.applicationLink,
                "contributorEmail": job.contributorEmail,
                "contributorName": job.contributor,
                "datePosted": job.date
            }
        )

        run_background_task(job)

        return JSONResponse(content={"message": "Job posted successfully"}, status_code=200)
    except Exception as e:
        return JSONResponse(content={"message":f"failed to post job: {e}"}, status_code=404)
    
@app.get("/get-jobs")
async def get_jobs():
    try:
        jobList = jobs.find({})
        jobsList = []
        for job in jobList:
            jobsList.append({
                "company": job["company"],
                "role": job["role"],
                "link": job["link"],
                "contributorEmail": job["contributorEmail"],
                "contributorName": job["contributorName"],
                "datePosted": job["datePosted"]
            })
        jobsList.reverse()
        return JSONResponse(content=jobsList, status_code=200)
    except Exception as e:
        return JSONResponse(content={"message":f"failed to get jobs: {e}"}, status_code=404)