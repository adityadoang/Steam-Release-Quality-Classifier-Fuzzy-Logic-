from fastapi import FastAPI, Request, Form, Depends, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from typing import List

from database import engine, Base, get_db
from models import DraftIndie
from fuzzy_logic import evaluate_quality

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Steam Release Quality Classifier")

# Setup templates
templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request, db: Session = Depends(get_db)):
    # Fetch all records initially
    games = db.query(DraftIndie).all()
    return templates.TemplateResponse(request, "index.html", {"games": games})

@app.post("/api/evaluate")
async def evaluate_game(
    request: Request,
    title: str = Form(...),
    bug_density: float = Form(...),
    fps: float = Form(...),
    wishlist: int = Form(...),
    remaining_budget: float = Form(...),
    db: Session = Depends(get_db)
):
    result = evaluate_quality(bug_density, fps, wishlist, remaining_budget)
    
    new_game = DraftIndie(
        title=title,
        bug_density=bug_density,
        fps=fps,
        wishlist=wishlist,
        remaining_budget=remaining_budget,
        score=result["score"],
        status=result["status"]
    )
    
    db.add(new_game)
    db.commit()
    db.refresh(new_game)
    
    # After submission, fetch updated list and render
    games = db.query(DraftIndie).all()
    return templates.TemplateResponse(request, "index.html", {
        "games": games,
        "message": f"Successfully evaluated '{title}'. Status: {result['status']} (Score: {result['score']})"
    })

@app.get("/api/query")
async def fuzzy_query(
    request: Request,
    status: str = "",
    db: Session = Depends(get_db)
):
    # Fuzzy Database Query endpoint
    query = db.query(DraftIndie)
    if status:
        query = query.filter(DraftIndie.status == status)
    
    games = query.all()
    return templates.TemplateResponse(request, "index.html", {"games": games, "selected_status": status})
