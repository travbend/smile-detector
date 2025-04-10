# Smile Detector

React/Python app which detects smile on user's face from the camera. Stores detected smile images on disk and metadata in a SQLite database.

## Running the App

1. Install npm and Node.js
1. Install the python requirements specified in backend/requirements.txt
1. Open a terminal window in the "backend" directory and run "python -m main" (or python3)
1. Open a terminal window in the "frontend" directory and run "npm install next@latest react@latest react-dom@latest" then run "npm run dev"

## Future Enhancements

1. Utilize a more robust database (e.g., PostgreSQL). SQLite works well for this small case.
1. Containerize the application and support multiple API instances.