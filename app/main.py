from typing import Optional
from fastapi import FastAPI, Response, status, HTTPException
from fastapi.params import Body
from pydantic import BaseModel
from random import randrange
import psycopg
from psycopg.rows import dict_row
import time

app = FastAPI()

class Post(BaseModel):
    title: str
    content: str
    published: bool = True
    rating: Optional[int] = None

while True:
    try:
        conn = psycopg.connect(host="localhost", dbname="fastapi", user='postgres', password='postgrespass', 
                               row_factory=dict_row)
        cursor = conn.cursor()
        print("Successfully connected to database")
        break
    except Exception as error:
        print("Can't connect to database")
        print("Error: " + str(error))
        time.sleep(5)


my_posts = [
    {"id": 1, "title": "Title of post 1", "content": "Content of post 1"},
    {"id": 2, "title": "Fave foods", "content": "I like pizza"}
]

def find_post(id):
    for post in my_posts:
        if post["id"] == id:
            return post
    return None

def find_post_index(id):
    for i, post in enumerate(my_posts):
        if post["id"] == id:
            return i
        print(i)
    return None

@app.get("/")
def root():
    return {"message": "welcome to my api"}

@app.get("/posts")
def get_posts():
    cursor.execute("""SELECT * FROM posts""")
    posts = cursor.fetchall()
    return {"data": posts}

@app.post("/posts", status_code = status.HTTP_201_CREATED)
def create_posts(new_post: Post):
    cursor.execute("""INSERT INTO posts (title, content, published) VALUES (%s, %s, %s) RETURNING *""", 
                   (new_post.title, new_post.content, new_post.published))
    new_post = cursor.fetchone()
    conn.commit()
    return {"data": new_post}

@app.get("/posts/{id}")
def get_post(id: int):
    cursor.execute("""SELECT * FROM posts WHERE id = %s""", [str(id)])
    post = cursor.fetchone()
    if not post:
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND, detail = f"Post with id: {id} was not found")
        # response.status_code = status.HTTP_404_NOT_FOUND
        # post = f"Post with id: {id} doesn't exist"
    return {"post_detail": post}

@app.delete("/posts/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id: int):
    cursor.execute("""DELETE FROM posts WHERE id = %s RETURNING * """, [str(id)])
    post = cursor.fetchone()
    conn.commit()
    if not post: 
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail = f"Post with id: {id} does not exist")
    return Response(status_code=status.HTTP_204_NO_CONTENT)

@app.put("/posts/{id}")
def update_post(id:int, post: Post):
    cursor.execute("""UPDATE posts SET title = %s, content = %s, published = %s WHERE id = %s RETURNING *""", 
                   [post.title, post.content, str(post.published), str(id)])
    updated_post = cursor.fetchone()
    conn.commit()

    if not updated_post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail = f"Post with id: {id} does not exist")
    return {"data": updated_post}