import sqlite3
from database import DATABASE_URL, init_db
from fuzzy_logic import evaluate_quality

# Create the database tables
init_db()

mock_games = [
    {
        "title": "Cosmic Survivor",
        "bug_density": 1.5,
        "fps": 60.0,
        "wishlist": 25000,
        "remaining_budget": 50.0
    },
    {
        "title": "Buggy Mess 3D",
        "bug_density": 12.0,
        "fps": 15.0,
        "wishlist": 1000,
        "remaining_budget": 5.0
    },
    {
        "title": "Mediocre RPG",
        "bug_density": 5.0,
        "fps": 30.0,
        "wishlist": 12000,
        "remaining_budget": 20.0
    },
    {
        "title": "Hidden Gem",
        "bug_density": 0.5,
        "fps": 45.0,
        "wishlist": 4000,
        "remaining_budget": 15.0
    },
    {
        "title": "Overhyped Trash",
        "bug_density": 9.0,
        "fps": 25.0,
        "wishlist": 30000,
        "remaining_budget": 80.0
    }
]

def seed_db():
    conn = sqlite3.connect(DATABASE_URL)
    cursor = conn.cursor()
    
    # Check if we already have data
    cursor.execute("SELECT COUNT(*) FROM draft_indie")
    count = cursor.fetchone()[0]
    
    if count == 0:
        for game in mock_games:
            # Evaluate fuzzy quality
            result = evaluate_quality(
                game['bug_density'],
                game['fps'],
                game['wishlist'],
                game['remaining_budget']
            )
            
            cursor.execute(
                """
                INSERT INTO draft_indie (title, bug_density, fps, wishlist, remaining_budget, score, status)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (game['title'], game['bug_density'], game['fps'], game['wishlist'], game['remaining_budget'], result['score'], result['status'])
            )
        conn.commit()
        print("Database seeded with mock games.")
    else:
        print("Database already contains data.")
    conn.close()

if __name__ == "__main__":
    seed_db()
