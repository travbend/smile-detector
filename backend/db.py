import sqlite3
import os
from datetime import datetime
from config import settings

def connect():
    conn = sqlite3.connect(os.path.join(settings.app_data_directory, settings.db_file_name))
    conn.row_factory = sqlite3.Row
    return conn

def table_exists(table_name):
    with connect() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name=?
        """, (table_name,))
        return cursor.fetchone() is not None

def init():
    with connect() as conn:
        cursor = conn.cursor()

        if not table_exists("detection"):
            cursor.execute("""CREATE TABLE detection (id INTEGER PRIMARY KEY AUTOINCREMENT, created_at TEXT, 
                           has_smile BOOLEAN, file_name TEXT, x INTEGER, y INTEGER, w INTEGER, h INTEGER)""")

def createDetection(created_at: datetime, has_smile: bool, file_name: str, x: int, y: int, w: int, h: int):
    with connect() as conn:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO detection (created_at, has_smile, file_name, x, y, w, h) VALUES (?, ?, ?, ?, ?, ?, ?)", 
                    (created_at, has_smile, file_name, x, y, w, h))
        return cursor.lastrowid
    
def getDetectionFilename(id: int):
    with connect() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT file_name FROM detection WHERE id = ?", (id,))
        result = cursor.fetchone()

        if result is None:
            return None
        
        return result["file_name"]

def getLatestDetections(before_id: int = None, batch_size: int = 10):
    if batch_size is None:
        batch_size = 10

    with connect() as conn:
        cursor = conn.cursor()

        if before_id is None:
            cursor.execute("SELECT * FROM detection ORDER BY id DESC")
        else:
            cursor.execute("SELECT * FROM detection WHERE id < ? ORDER BY id DESC", (before_id,))

        return cursor.fetchmany(batch_size)