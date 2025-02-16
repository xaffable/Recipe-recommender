# This is a sample Python script.
from http.client import HTTPException
import random

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import uuid
from datetime import timezone
import datetime
import psycopg2
from psycopg2 import pool
import pandas as pd

db_connection_pool = psycopg2.pool.SimpleConnectionPool(1,15,database="recipe_recommender",
                                user="backend_user",
                                password="uy4c2qnypT8fNSx",
                                host="localhost",
                                port="5432")


def return_connection(conn, cursor):
    cursor.close()
    db_connection_pool.putconn(conn)


if __name__ == "__main__":
    uvicorn.run("main:api", host="127.0.0.1", port=8000, reload=True)
api = FastAPI()
api_base_url = "/api/v1/"

#Add CORS to allow origin from different port
api.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    #allow_origins=["http://localhost:63342","http://localhost:8000"],  # Frontend origin
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

    # Add cookie to users table in DB.
    try:
        conn = db_connection_pool.getconn()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO recipe_recommender.users (id,cookie_expiration) VALUES (%s, %s)
        """, (str(user_uuid), formatted_expiration_time))
        conn.commit()
        return {"UUID":user_uuid,
                "Expiration":formatted_expiration_time,
                "Message":"New cookie has been generated."
                }
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        return_connection(conn, cursor)


#Renew existing cookie expiration date.
@api.put(api_base_url+"renew-cookie")
async def renew_cookie(UUID: uuid.UUID):
    user_uuid = UUID
    expiration_time = datetime.datetime.now(timezone.utc) + datetime.timedelta(days=365)
    formatted_expiration_time = expiration_time.strftime('%a, %d %b %Y %H:%M:%S GMT')

    try:
        conn = db_connection_pool.getconn()
        cursor = conn.cursor()
        # Update cookie expiration in users table in DB.
        cursor.execute("UPDATE recipe_recommender.users SET cookie_expiration = %s WHERE id = %s", (formatted_expiration_time, str(user_uuid)))
        conn.commit()
        return {"UUID":user_uuid,
            "Expiration":formatted_expiration_time,
            "Message":"Cookie renewed successfully."
            }
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        return_connection(conn, cursor)

#Retrieve a new recommended recipe
@api.get(api_base_url+"get-recommended-recipe")
async def get_recipe(UUID: uuid.UUID):
        user_uuid = UUID
        conn = db_connection_pool.getconn()
        cursor = conn.cursor()
        try:
            cursor.execute(
                "SELECT liked_recipes,disliked_recipes,liked_ingredients,disliked_ingredients FROM recipe_recommender.users WHERE id = %s",
                (str(user_uuid),))
            user_data_check = cursor.fetchone()[0]
            if user_data_check is None or user_data_check == []:
            #if user_data_check is None or all(value is None for value in user_data_check):
                cursor.execute("""
                    SELECT MAX(id) FROM recipe_recommender.recipes
                """)
                max_id = cursor.fetchone()[0]
                random_recipe = random.randint(1,max_id)
                cursor.execute("SELECT * FROM recipe_recommender.recipes WHERE id = %s", (int(random_recipe),))
                recipe = cursor.fetchone()
                return {"recipe_id":recipe[0],
                    "name": recipe[1],
                    "author": recipe[2],
                    "published_date": recipe[3],
                    "description": recipe[4],
                    "calories": recipe[5],
                    "fat": recipe[6],
                    "saturated_fat": recipe[7],
                    "cholesterol": recipe[8],
                    "sodium": recipe[9],
                    "carbs": recipe[10],
                    "fiber": recipe[11],
                    "sugar": recipe[12],
                    "protein": recipe[13],
                    "servings": recipe[14],
                    "instructions": recipe[15],
                    "image": recipe[16],
                    "ingredient_quantities": recipe[17],
                    "ingredients": recipe[18],
                    }
            else:
                return {"Message": "Recipe generated by Algorithm will be displayed here."
                        }
        except Exception as e:
            conn.rollback()
            raise HTTPException(status_code=500, detail=str(e))
        finally:
            return_connection(conn, cursor)


#Retrieve a specific recipe
@api.get(api_base_url+"get-recipe")
async def get_recipe(recipe_id: int):
        conn = db_connection_pool.getconn()
        cursor = conn.cursor()
        try:
            cursor.execute(
                "SELECT * FROM recipe_recommender.recipes WHERE id = %s",
                (int(recipe_id),))
            recipe = cursor.fetchone()
            return {"recipe_id":recipe[0],
                    "name": recipe[1],
                    "author": recipe[2],
                    "published_date": recipe[3],
                    "description": recipe[4],
                    "calories": recipe[5],
                    "fat": recipe[6],
                    "saturated_fat": recipe[7],
                    "cholesterol": recipe[8],
                    "sodium": recipe[9],
                    "carbs": recipe[10],
                    "fiber": recipe[11],
                    "sugar": recipe[12],
                    "protein": recipe[13],
                    "servings": recipe[14],
                    "instructions": recipe[15],
                    "image": recipe[16],
                    "ingredient_quantities": recipe[17],
                    "ingredients": recipe[18],
                    }
        except Exception as e:
            conn.rollback()
            raise HTTPException(status_code=500, detail=str(e))
        finally:
            return_connection(conn, cursor)

@api.get(api_base_url+"get-liked-recipes")
async def get_liked_recipes(UUID: uuid.UUID, page: int = 1, per_page: int = 12):
    sql_offset = per_page * (page - 1)
    user_uuid = UUID
    conn = db_connection_pool.getconn()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "SELECT r.id AS recipe_id, r.name, r.images FROM recipe_recommender.recipes r JOIN recipe_recommender.users i ON r.id = ANY(i.liked_recipes) WHERE i.id = %s LIMIT %s OFFSET %s",
            (str(user_uuid), per_page, sql_offset))
        liked_recipes = cursor.fetchall()
        return [{"recipe_id": row[0],
                "name": row[1],
                "image": row[2]} for row in liked_recipes]
    finally:
        return_connection(conn, cursor)

@api.get(api_base_url+"get-disliked-recipes")
async def get_liked_recipes(UUID: uuid.UUID):
    user_uuid = UUID
    conn = db_connection_pool.getconn()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT disliked_recipes FROM recipe_recommender.users WHERE id = %s",
        (str(user_uuid),))
    disliked_recipes = cursor.fetchone()
    return {"disliked_recipes": disliked_recipes[0]
}

@api.get(api_base_url+"like-recipe")
async def like_recipe(UUID: uuid.UUID, recipe_id: int):
    user_uuid = UUID
    conn = db_connection_pool.getconn()
    cursor = conn.cursor()
    try:
        cursor.execute("UPDATE recipe_recommender.users SET liked_recipes = CASE WHEN %s = ANY(liked_recipes) THEN liked_recipes ELSE array_append(liked_recipes, %s) END, disliked_recipes = array_remove(disliked_recipes, %s)  WHERE id = %s",
               (recipe_id, recipe_id, recipe_id, str(user_uuid)))
        conn.commit()
        return {"Message": "Added recipe ID: " + str(recipe_id) + " to liked recipes for user ID: " + str(user_uuid)}
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        return_connection(conn, cursor)

@api.get(api_base_url+"dislike-recipe")
async def like_recipe(UUID: uuid.UUID, recipe_id: int):
    user_uuid = UUID
    conn = db_connection_pool.getconn()
    cursor = conn.cursor()
    try:
        cursor.execute("UPDATE recipe_recommender.users SET disliked_recipes = CASE WHEN %s = ANY(disliked_recipes) THEN disliked_recipes ELSE array_append(disliked_recipes, %s) END, liked_recipes = array_remove(liked_recipes, %s)  WHERE id = %s",
               (recipe_id, recipe_id, recipe_id, str(user_uuid)))
        conn.commit()
        return {"Message": "Added recipe ID: " + str(recipe_id) + " to liked recipes for user ID: " + str(user_uuid)}
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        return_connection(conn, cursor)


@api.get(api_base_url+"get-graphs")
async def read_root():
    return {"Message": "This is where graphs will be."
    }

