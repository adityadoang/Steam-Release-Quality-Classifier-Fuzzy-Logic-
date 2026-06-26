import sqlite3
from database import init_db
from fuzzy_logic import evaluate_quality

def seed_db():
    print("Initializing database...")
    init_db(reset=True)
    
    sample_games = [
        {
            "title": "Cyberpunk: Bug Edition",
            "bug_density": 12.5,
            "fps": 18.0,
            "wishlist": 45000,
            "remaining_budget": 8.0
        },
        {
            "title": "Hollow Knight: Silksoon",
            "bug_density": 0.5,
            "fps": 95.0,
            "wishlist": 35000,
            "remaining_budget": 48.0
        },
        {
            "title": "Stardew Valley Clone",
            "bug_density": 1.2,
            "fps": 60.0,
            "wishlist": 12000,
            "remaining_budget": 30.0
        },
        {
            "title": "Farming Sim 2026",
            "bug_density": 4.5,
            "fps": 40.0,
            "wishlist": 2000,
            "remaining_budget": 15.0
        },
        {
            "title": "Super Meat Boy Forever 2",
            "bug_density": 5.0,
            "fps": 85.0,
            "wishlist": 18000,
            "remaining_budget": 42.0
        },
        {
            "title": "Rough Prototype RPG",
            "bug_density": 9.5,
            "fps": 28.0,
            "wishlist": 800,
            "remaining_budget": 5.0
        }
    ]
    
    conn = sqlite3.connect("./indie_games.db")
    cursor = conn.cursor()
    
    print("Seeding sample games...")
    for game in sample_games:
        # Evaluate using fuzzy engine
        res = evaluate_quality(
            game["bug_density"], 
            game["fps"], 
            game["wishlist"], 
            game["remaining_budget"]
        )
        
        m = res["memberships"]
        
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
                game["title"],
                game["bug_density"],
                game["fps"],
                game["wishlist"],
                game["remaining_budget"],
                res["score"],
                res["status"],
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
        print(f"Added '{game['title']}' with verdict: {res['status']} (Score: {res['score']})")
        
    conn.commit()
    conn.close()
    print("Database seeding completed successfully!")

if __name__ == "__main__":
    seed_db()
