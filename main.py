from fastapi import FastAPI, Request, Form, Depends, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import sqlite3
from typing import List

from database import init_db, get_db
from fuzzy_logic import evaluate_quality

# Create tables
init_db()

app = FastAPI(title="Steam Release Quality Classifier")

# Setup templates
templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request, db: sqlite3.Connection = Depends(get_db)):
    # Fetch all records initially
    cursor = db.cursor()
    cursor.execute("SELECT * FROM draft_indie")
    games = cursor.fetchall()
    return templates.TemplateResponse(request, "index.html", {"games": games})

@app.post("/api/evaluate")
async def evaluate_game(
    request: Request,
    title: str = Form(...),
    bug_density: float = Form(...),
    fps: float = Form(...),
    wishlist: int = Form(...),
    remaining_budget: float = Form(...),
    db: sqlite3.Connection = Depends(get_db)
):
    result = evaluate_quality(bug_density, fps, wishlist, remaining_budget)
    
    cursor = db.cursor()
    cursor.execute(
        """
        INSERT INTO draft_indie (title, bug_density, fps, wishlist, remaining_budget, score, status)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (title, bug_density, fps, wishlist, remaining_budget, result["score"], result["status"])
    )
    db.commit()
    
    # After submission, fetch updated list and render
    cursor.execute("SELECT * FROM draft_indie")
    games = cursor.fetchall()
    return templates.TemplateResponse(request, "index.html", {
        "games": games,
        "message": f"Successfully evaluated '{title}'. Status: {result['status']} (Score: {result['score']})"
    })

@app.get("/api/query")
async def fuzzy_query(
    request: Request,
    status: str = "",
    db: sqlite3.Connection = Depends(get_db)
):
    # Fuzzy Database Query endpoint
    cursor = db.cursor()
    if status:
        cursor.execute("SELECT * FROM draft_indie WHERE status = ?", (status,))
    else:
        cursor.execute("SELECT * FROM draft_indie")
    
    games = cursor.fetchall()
    return templates.TemplateResponse(request, "index.html", {"games": games, "selected_status": status})
