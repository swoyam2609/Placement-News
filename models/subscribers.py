from pydantic import BaseModel

class Subscriber(BaseModel):
    name:str
    email:str