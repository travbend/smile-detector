from fastapi import FastAPI, UploadFile, HTTPException
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import uvicorn
import cv2
import os
from uuid import uuid4
import numpy as np
import db
from datetime import datetime, timezone
from config import settings

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Init environment
    init_environment()
    yield

def init_environment():
    os.makedirs(os.path.join(os.getcwd(), settings.app_data_directory, settings.images_directory), exist_ok=True)
    db.init()

# Init API
app = FastAPI(lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:8000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def home():
    return # For frontend to test if backend is up

@app.post("/detect-smile")
async def detectSmile(file: UploadFile):
    if file.size > settings.max_image_size:
        raise HTTPException(status_code=400, detail="Image is too large") 
    
    bytes = await file.read()
    nparr = np.frombuffer(bytes, np.uint8)

    image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    if image is None:
        raise ValueError("Could not decode image")
    
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    smile_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_smile.xml')
    
    smiles = smile_cascade.detectMultiScale(
        gray,
        scaleFactor=1.7,
        minNeighbors=22,
        minSize=(25, 25)
    )
    
    has_smile = False
    (x, y, w, h) = (None, None, None, None)
    if len(smiles) > 0:
        has_smile = True
        (x, y, w, h) = tuple(map(int, smiles[0]))
        cv2.rectangle(image, (x, y), (x+w, y+h), (32, 223, 255), 2) #color matches UI

    file_path = os.path.join(os.getcwd(), settings.app_data_directory, settings.images_directory, str(uuid4()) + ".png")
    cv2.imwrite(file_path, image)

    id = db.createDetection(datetime.now(timezone.utc), has_smile, file_path, x, y, w, h)
    
    return {
        'id': id,
        'coordinates': {
            'x': x,
            'y': y,
            'w': w,
            'h': h
        }
    }

@app.get("/smile-image")
async def getImage(id: int):
    file_path = db.getDetectionFilename(id)

    if file_path is None:
        raise HTTPException(status_code=404, detail="Image not found")

    return FileResponse(
        path=file_path,
        filename="image.png",
        media_type='image/png'
    )

@app.get("/latest-detections")
async def getLatestDetections(before_id: int = None):
    return db.getLatestDetections(before_id)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)