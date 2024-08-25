from pydantic import BaseModel
from datetime import datetime

class Job(BaseModel):
    companyName: str
    role: str
    applicationLink : str
    date : datetime = None
    contributor : str
    contributorEmail: str