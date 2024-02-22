import os
import logging
import pathlib
import json
import hashlib
import sqlite3
from fastapi import FastAPI, Form, HTTPException, UploadFile, File
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path

app = FastAPI()
logger = logging.getLogger("uvicorn")
logger.level = logging.INFO

# Path configuration
images = pathlib.Path(__file__).parent.resolve() / "images"
sqlite3_file = pathlib.Path(__file__).parent.parent.resolve()

# CORS configuration
origins = [os.environ.get("FRONT_URL", "http://localhost:3000")]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=False,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

# Load data from items.json and populate the database
with open("items.json", "r") as f:
    items_data = json.load(f)

# Connect to the SQLite database
conn = sqlite3.connect(f'{sqlite3_file}/db/mercari.sqlite3')
c = conn.cursor()

# Create categories table if it doesn't exist
c.execute('''CREATE TABLE IF NOT EXISTS categories (
             id INTEGER PRIMARY KEY AUTOINCREMENT,
             name TEXT)''')
# Extract unique category names from items_data
categories_data = set(item["category"] for item in items_data)

# Insert data into categories table
for category_name in categories_data:
    # Check if the category already exists in the categories table
    c.execute("SELECT id FROM categories WHERE name=?", (category_name,))
    existing_category = c.fetchone()
    if existing_category is None:
        # If the category does not exist, insert it into the categories table
        c.execute("INSERT INTO categories (name) VALUES (?)", (category_name,))
        
# Create items table if it doesn't exist
c.execute('''CREATE TABLE IF NOT EXISTS items (
             id INTEGER PRIMARY KEY AUTOINCREMENT,
             name TEXT,
             category TEXT,
             image_name TEXT)''')

# Insert data into items table
for item in items_data:
    category_id = c.execute("SELECT id FROM categories WHERE name=?", (item["category"],)).fetchone()[0]
    c.execute("INSERT INTO items (name, category, image_name) VALUES (?, ?, ?)", (item["name"], item["category"], item["image_name"]))

# Commit changes and close connection
conn.commit()
conn.close()

@app.get("/")
def root():
    return {"message": "Hello, world!"}
    

@app.get("/items")
def get_items():
    try:
        conn = sqlite3.connect(f'{sqlite3_file}/db/mercari.sqlite3')
        c = conn.cursor()
        c.execute("SELECT * FROM items")
        items = c.fetchall()
        conn.close
        # with open("items.json", "r") as f:
        #     items = json.load(f)
        return {"items": items}
    except Exception as e:
        logger.error(f"An error occurred: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/items")
async def add_item(name: str = Form(...), category: str = Form(...), image: UploadFile = File(...)):
    try:
        # Read image contents
        contents = await image.read()

        # Generate unique image name
        image_name = hashlib.sha256(contents).hexdigest() + ".jpg"
        image_path = images / image_name
        image_path.write_bytes(contents)

        # Connect to the SQLite database
        conn = sqlite3.connect(f'{sqlite3_file}/db/mercari.sqlite3')
        c = conn.cursor()

        # Check if category exists in the categories table
        c.execute("SELECT id FROM categories WHERE name=?", (category,))
        category_id = c.fetchone()

        # Close the cursor after fetching the category id
        c.close()

        # If category does not exist, insert it into the categories table
        if category_id is None:
            c = conn.cursor()  # Reopen the cursor
            c.execute("INSERT INTO categories (name) VALUES (?)", (category,))
            conn.commit()  # Commit the changes to the database
            category_id = c.lastrowid  # Get the id of the newly inserted category
            c.close()  # Close the cursor after inserting the category

        # Insert item into the items table
        c = conn.cursor()  # Reopen the cursor
        c.execute("INSERT INTO items (name, category, image_name) VALUES (?, ?, ?)", (name, category_id, image_name))
        conn.commit()

        # Close the database connection
        conn.close()

        return {"message": "Item added successfully"}
    
    except Exception as e:
        logger.error(f"An error occurred: {e}")
        raise HTTPException(status_code=500, detail=str(e))

        # items = []
        # if Path("items.json").exists():
        #     with open("items.json", "r") as f:
        #         data = json.load(f)
        #         if isinstance(data, list):
        #             items = data
        # item_id = len(items) + 1
        # item = {"id": item_id, "name": name, "category": category, "image_name": image_name}
        # items.append(item)
        # with open("items.json", "w") as f:
        #     json.dump(items, f)
    #     return {"items": items}

@app.get("/image/{image_name}")
async def get_image(image_name):
    try:
        image = images / image_name

        if not image_name.endswith(".jpg"):
            raise HTTPException(status_code=400, detail="Image path does not end with .jpg")

        if not image.exists():
            logger.debug(f"Image not found: {image}")
            image = images / "default.jpg"

        return FileResponse(str(image))
    except Exception as e:
        logger.error(f"An error occurred: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    
@app.get("/items/{item_id}")
def get_item(item_id: int):
    try:
        conn = sqlite3.connect(f'{sqlite3_file}/db/mercari.sqlite3')
        c = conn.cursor()
        c.execute("SELECT * FROM items WHERE id=?", (item_id,))
        item = c.fetchone()
        conn.close()
        if item is None:
            raise HTTPException(status_code=404, detail="Item not found")
        return {"item": item}
    except Exception as e:
        logger.error(f"An error occurred: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/search")
def search_items(keyword: str):
    try:
        # Connect to the SQLite database
        conn = sqlite3.connect(f'{sqlite3_file}/db/mercari.sqlite3')
        c = conn.cursor()

        # Fetch items from the database based on the keyword
        c.execute("SELECT name, category FROM items WHERE name LIKE ?", ('%' + keyword + '%',))
        items = c.fetchall()

        # Close the database connection
        conn.close()

        if not items:
            return {"items": []}  # Return an empty list if no items are found
        
        # Format the items into a list of dictionaries without the id field
        formatted_items = [{"name": item[0], "category": item[1]} for item in items]

        return {"items": formatted_items}
    except sqlite3.Error as e:
        logger.error(f"A SQLite error occurred: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}")
        raise HTTPException(status_code=500, detail=str(e))
