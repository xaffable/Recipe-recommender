# This is a sample Python script.

# Press ⌃R to execute it or replace it with your code.

# Press Double ⇧ to search everywhere for classes, files, tool windows, actions, and settings.

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import uuid
from datetime import timezone
import datetime


if __name__ == "__main__":
    uvicorn.run("main:api", host="127.0.0.1", port=8000, reload=True)
api = FastAPI()
api_base_url = "/api/v1/"

#Add CORS to allow origin from different port
api.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:63343"],  # Frontend origin
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

#API request to return UUID for user tracking cookie.
@api.get(api_base_url+"generate-cookie")
async def read_root():
    # Generate a UUID
    user_uuid = uuid.uuid4()
    expiration_time = datetime.datetime.now(timezone.utc) + datetime.timedelta(days=365)
    formatted_expiration_time = expiration_time.strftime('%a, %d %b %Y %H:%M:%S GMT')
    return {"UUID":user_uuid,
            "Expiration":formatted_expiration_time
            }

#Renew existing cookie expiration date.
@api.put(api_base_url+"renew-cookie")
async def renew_cookie(UUID: uuid.UUID):
    # Generate a UUID
    user_uuid = UUID
    expiration_time = datetime.datetime.now(timezone.utc) + datetime.timedelta(days=365)
    formatted_expiration_time = expiration_time.strftime('%a, %d %b %Y %H:%M:%S GMT')
    return {"UUID":user_uuid,
            "Expiration":formatted_expiration_time,
            "Message":"Cookie renewed successfully."
            }

@api.get(api_base_url+"recipe")
async def read_root():
    return {"recipe_id":"Congrats! This is your first API!",
            "name":"Sample name",
            "author":"John Doe",
            "published_date":"01-01-2020",
            "description":"Sample description.",
            "image":"https://example.com/",
            "ingredient_quantities":"1",
            "ingredients":"Water",
            "calories":123,
            "fat":5,
            "saturated_fat":0.5,
            "cholesterol":0,
            "sodium":1,
            "carbs":1,
            "fiber":1,
            "sugar":1,
            "protein":1,
            "servings":"1",
            "instructions":"Sample instructions"
            }
