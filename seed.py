from database import engine, Base, SessionLocal
from models import DraftIndie
from fuzzy_logic import evaluate_quality

# Create the database tables
Base.metadata.create_all(bind=engine)

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
    db = SessionLocal()
    # Check if we already have data
    if db.query(DraftIndie).count() == 0:
        for game in mock_games:
            # Evaluate fuzzy quality
            result = evaluate_quality(
                game['bug_density'],
                game['fps'],
                game['wishlist'],
                game['remaining_budget']
            )
            
            db_game = DraftIndie(
                title=game['title'],
                bug_density=game['bug_density'],
                fps=game['fps'],
                wishlist=game['wishlist'],
                remaining_budget=game['remaining_budget'],
                score=result['score'],
                status=result['status']
            )
            db.add(db_game)
        db.commit()
        print("Database seeded with mock games.")
    else:
        print("Database already contains data.")
    db.close()

if __name__ == "__main__":
    seed_db()
