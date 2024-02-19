import os
import logging
import pathlib
import json
import hashlib
from fastapi import FastAPI, Form, HTTPException, UploadFile, File
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path

app = FastAPI()
logger = logging.getLogger("uvicorn")
logger.level = logging.INFO
images = pathlib.Path(__file__).parent.resolve() / "images"
origins = [os.environ.get("FRONT_URL", "http://localhost:3000")]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=False,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"message": "Hello, world!"}

@app.get("/items")
def get_items():
    with open("items.json", "r") as f:
        items = json.load(f)
    return {"items": items}

@app.post("/items")
async def add_item(name: str = Form(...), category: str = Form(...), image: UploadFile = File(...)):
    try:
        contents = await image.read()
        image_name = hashlib.sha256(contents).hexdigest() + ".jpg"
        image_path = images / image_name
        image_path.write_bytes(contents)

        items = []
        if Path("items.json").exists():
            with open("items.json", "r") as f:
                data = json.load(f)
                if isinstance(data, list):
                    items = data

        item_id = len(items) + 1
        item = {"id": item_id, "name": name, "category": category, "image_name": image_name}

        items.append(item)

        with open("items.json", "w") as f:
            json.dump(items, f)

        return {"items": items}
    except Exception as e:
        logger.error(f"An error occurred: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/image/{image_name}")
async def get_image(image_name):
    image = images / image_name

    if not image_name.endswith(".jpg"):
        raise HTTPException(status_code=400, detail="Image path does not end with .jpg")

    if not image.exists():
        logger.debug(f"Image not found: {image}")
        image = images / "default.jpg"

    return FileResponse(str(image))

@app.get("/items/{item_id}")
def get_item(item_id: int):
    try:
        with open("items.json", "r") as f:
            items = json.load(f)
        for item in items:
            if item['id'] == item_id:
                return item  # return the item directly
        raise HTTPException(status_code=404, detail="Item not found")
    except Exception as e:
        logger.error(f"An error occurred: {e}")
        raise HTTPException(status_code=500, detail=str(e))
