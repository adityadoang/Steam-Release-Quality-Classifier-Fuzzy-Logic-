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
app.mount("/static", StaticFiles(directory="static"), name="static")

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
    
    # Convert sqlite3.Row to dict so we can work with it flexibly in templates
    games_list = [dict(g) for g in games]
    return games_list, total_pages, total

def get_fuzzy_games(
    db: sqlite3.Connection,
    bug_density_fuzzy: str = "",
    fps_fuzzy: str = "",
    wishlist_fuzzy: str = "",
    budget_fuzzy: str = "",
    operator: str = "AND",
    alpha_cut: float = 0.0,
    page: int = 1
):
    filters = {}
    if bug_density_fuzzy: filters["bug_density"] = bug_density_fuzzy
    if fps_fuzzy: filters["fps"] = fps_fuzzy
    if wishlist_fuzzy: filters["wishlist"] = wishlist_fuzzy
    if budget_fuzzy: filters["budget"] = budget_fuzzy
    
    cursor = db.cursor()
    
    if not filters:
        query = "SELECT *, 1.0 AS match_degree FROM draft_indie"
        count_query = "SELECT COUNT(*) FROM draft_indie"
        params = []
        count_params = []
    else:
        col_mapping = {
            "bug_density": "bug",
            "fps": "fps",
            "wishlist": "wishlist",
            "budget": "budget"
        }
        db_cols = [f"mu_{col_mapping[col_name]}_{fuzzy_val}" for col_name, fuzzy_val in filters.items()]
        
        # Hitung derajat kecocokan di SQL (Model Tahani)
        if len(db_cols) == 1:
            match_expr = db_cols[0]
        else:
            func = "MIN" if operator == "AND" else "MAX"
            match_expr = f"{func}({', '.join(db_cols)})"
            
        # Filter berdasarkan Alpha Cut
        # AND: col1 >= alpha AND col2 >= alpha
        # OR: col1 >= alpha OR col2 >= alpha
        where_op = " AND " if operator == "AND" else " OR "
        where_clause = where_op.join([f"{col} >= ?" for col in db_cols])
        
        query = f"SELECT *, {match_expr} AS match_degree FROM draft_indie WHERE {where_clause}"
        count_query = f"SELECT COUNT(*) FROM draft_indie WHERE {where_clause}"
        params = [alpha_cut] * len(db_cols)
        count_params = [alpha_cut] * len(db_cols)
        
    # Urutkan berdasarkan derajat kecocokan tertinggi
    if filters:
        query += " ORDER BY match_degree DESC, id DESC"
    else:
        query += " ORDER BY id DESC"
        
    # Hitung total data yang cocok
    cursor.execute(count_query, count_params)
    total = cursor.fetchone()[0]
    
    # Ambil data terpaginasi
    query += " LIMIT ? OFFSET ?"
    offset = (page - 1) * PAGE_SIZE
    params.extend([PAGE_SIZE, offset])
    
    cursor.execute(query, params)
    rows = cursor.fetchall()
    
    games_list = [dict(row) for row in rows]
    total_pages = max(1, (total + PAGE_SIZE - 1) // PAGE_SIZE)
    
    return games_list, total_pages, total

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request, page: int = 1, message: Optional[str] = None, db: sqlite3.Connection = Depends(get_db)):
    games, total_pages, total_items = get_paginated_games(db, page=page)
    return templates.TemplateResponse(request, "index.html", {
        "games": games,
        "current_page": page,
        "total_pages": total_pages,
        "total_items": total_items,
        "message": message,
        "query_type": "standard",
        "selected_status": ""
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
    m = result["memberships"]
    
    cursor = db.cursor()
    cursor.execute(
        """
        INSERT INTO draft_indie (
            title, bug_density, fps, wishlist, remaining_budget, score, status,
            mu_bug_sangat_bersih, mu_bug_wajar, mu_bug_rusak,
            mu_fps_patah_patah, mu_fps_stabil, mu_fps_lancar,
            mu_wishlist_sedikit, mu_wishlist_menjanjikan, mu_wishlist_meledak,
            mu_budget_kritis, mu_budget_aman, mu_budget_melimpah,
            mu_quality_tunda, mu_quality_akses_awal, mu_quality_siap_rilis
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            title,
            bug_density,
            fps,
            wishlist,
            remaining_budget,
            result["score"],
            result["status"],
            m["mu_bug_sangat_bersih"],
            m["mu_bug_wajar"],
            m["mu_bug_rusak"],
            m["mu_fps_patah_patah"],
            m["mu_fps_stabil"],
            m["mu_fps_lancar"],
            m["mu_wishlist_sedikit"],
            m["mu_wishlist_menjanjikan"],
            m["mu_wishlist_meledak"],
            m["mu_budget_kritis"],
            m["mu_budget_aman"],
            m["mu_budget_melimpah"],
            m["mu_quality_tunda"],
            m["mu_quality_akses_awal"],
            m["mu_quality_siap_rilis"]
        )
    )
    db.commit()
    
    import urllib.parse
    msg = f"Berhasil mengevaluasi '{title}'. Status: {result['status']} (Skor: {result['score']})"
    url_msg = urllib.parse.quote(msg)
    
    return RedirectResponse(url=f"/?message={url_msg}", status_code=303)

@app.get("/api/query")
async def fuzzy_query(
    request: Request,
    query_type: str = "standard",
    status: str = "",
    bug_density_fuzzy: str = "",
    fps_fuzzy: str = "",
    wishlist_fuzzy: str = "",
    budget_fuzzy: str = "",
    operator: str = "AND",
    alpha_cut: float = 0.0,
    page: int = 1,
    db: sqlite3.Connection = Depends(get_db)
):
    if query_type == "fuzzy":
        games, total_pages, total_items = get_fuzzy_games(
            db, bug_density_fuzzy, fps_fuzzy, wishlist_fuzzy, budget_fuzzy, operator, alpha_cut, page
        )
    else:
        games, total_pages, total_items = get_paginated_games(db, status, page)
        
    return templates.TemplateResponse(request, "index.html", {
        "games": games,
        "current_page": page,
        "total_pages": total_pages,
        "total_items": total_items,
        "query_type": query_type,
        "selected_status": status,
        "bug_density_fuzzy": bug_density_fuzzy,
        "fps_fuzzy": fps_fuzzy,
        "wishlist_fuzzy": wishlist_fuzzy,
        "budget_fuzzy": budget_fuzzy,
        "operator": operator,
        "alpha_cut": alpha_cut
    })
