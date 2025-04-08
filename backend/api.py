from fastapi import FastAPI, UploadFile, HTTPException
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import cv2
import os
from uuid import uuid4
import numpy as np
import db
from datetime import datetime, timezone

IMAGE_DIRECTORY = "images"
os.makedirs(IMAGE_DIRECTORY, exist_ok=True)

db.init()
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:8000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/detect-smile")
async def detectSmile(file: UploadFile):
    if file.size > 10000000: # TODO
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
        (x, y, w, h) = smiles[0]
        (x, y, w, h) = (int(x), int(y), int(w), int(h))
        cv2.rectangle(image, (x, y), (x+w, y+h), (0, 255, 0), 2)

    file_path = os.path.join(IMAGE_DIRECTORY, str(uuid4()) + ".png")
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

@app.get("/smile-image/{id}")
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
async def getLatestDetections():
    return db.getLatestDetections()


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)