from fastapi import FastAPI, Request, Form, Depends, HTTPException, Query
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import sqlite3
from typing import List, Optional

from database import init_db, get_db
from fuzzy_logic import evaluate_quality

# Create tables
init_db()

app = FastAPI(title="Steam Release Quality Classifier")

# Setup templates
templates = Jinja2Templates(directory="templates")

PAGE_SIZE = 5

def get_paginated_games(db: sqlite3.Connection, status: str = "", page: int = 1):
    cursor = db.cursor()
    offset = (page - 1) * PAGE_SIZE
    
    if status:
        cursor.execute("SELECT COUNT(*) FROM draft_indie WHERE status = ?", (status,))
        total = cursor.fetchone()[0]
        cursor.execute("SELECT * FROM draft_indie WHERE status = ? ORDER BY id DESC LIMIT ? OFFSET ?", (status, PAGE_SIZE, offset))
    else:
        cursor.execute("SELECT COUNT(*) FROM draft_indie")
        total = cursor.fetchone()[0]
        cursor.execute("SELECT * FROM draft_indie ORDER BY id DESC LIMIT ? OFFSET ?", (PAGE_SIZE, offset))
        
    games = cursor.fetchall()
    total_pages = max(1, (total + PAGE_SIZE - 1) // PAGE_SIZE)
    return games, total_pages, total

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request, page: int = 1, message: Optional[str] = None, db: sqlite3.Connection = Depends(get_db)):
    games, total_pages, total_items = get_paginated_games(db, page=page)
    return templates.TemplateResponse(request, "index.html", {
        "games": games,
        "current_page": page,
        "total_pages": total_pages,
        "total_items": total_items,
        "message": message
    })

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
    
    import urllib.parse
    msg = f"Successfully evaluated '{title}'. Status: {result['status']} (Score: {result['score']})"
    url_msg = urllib.parse.quote(msg)
    
    return RedirectResponse(url=f"/?message={url_msg}", status_code=303)

@app.get("/api/query")
async def fuzzy_query(
    request: Request,
    status: str = "",
    page: int = 1,
    db: sqlite3.Connection = Depends(get_db)
):
    games, total_pages, total_items = get_paginated_games(db, status, page)
    return templates.TemplateResponse(request, "index.html", {
        "games": games,
        "current_page": page,
        "total_pages": total_pages,
        "total_items": total_items,
        "selected_status": status
    })
