from fastapi import FastAPI, UploadFile, HTTPException
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import cv2
import numpy as np
from io import BytesIO

app = FastAPI()

origins = [
    "http://localhost:3000",
    "http://localhost:8000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def test():
    return "Testing 123"

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
    
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    smile_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_smile.xml')
    
    faces = face_cascade.detectMultiScale(
        gray, 
        scaleFactor=1.1, 
        minNeighbors=5, 
        minSize=(30, 30)
    )
    
    smile_coordinates = []
    
    for (x, y, w, h) in faces:
        roi_gray = gray[y:y+h, x:x+w]
        roi_color = image[y:y+h, x:x+w]
        
        smiles = smile_cascade.detectMultiScale(
            roi_gray,
            scaleFactor=1.7,
            minNeighbors=22,
            minSize=(25, 25)
        )
        
        for (sx, sy, sw, sh) in smiles:
            abs_x = x + sx
            abs_y = y + sy
            smile_coordinates.append((int(abs_x), int(abs_y), int(sw), int(sh)))
            
            cv2.rectangle(roi_color, (sx, sy), (sx+sw, sy+sh), (0, 255, 0), 2)
            cv2.putText(roi_color, 'Smile', (sx, sy-10),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)
    
    for (x, y, w, h) in faces:
        cv2.rectangle(image, (x, y), (x+w, y+h), (255, 0, 0), 2)

    success, encoded_image = cv2.imencode('.png', image)
    if not success:
        raise Exception("Failed to encode image")
    
    image_bytes = BytesIO(encoded_image.tobytes())
    
    # Return as streaming response
    return StreamingResponse(
        image_bytes,
        media_type="image/png",
        headers={"Content-Disposition": "inline; filename=image.png"}
    )
    
    return {
        'coordinates': smile_coordinates
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)