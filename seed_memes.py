from app import create_app
from app.tasks import fetch_and_store_memes
from app.models import db, Meme

def seed_memes():
    app = create_app()
    with app.app_context():
        db.create_all()

        current_count = Meme.query.count()
        if current_count >= 100:
            print(f"Database has {current_count} memes. Skipping seed.")
            return

        print(f"Database has {current_count} memes. Fetching more...")

        # Reuse the task logic, but loop until we have enough
        attempts = 0
        while Meme.query.count() < 100 and attempts < 10:
            attempts += 1
            print(f"Attempt {attempts}...")
            fetch_and_store_memes(limit=50)

        print(f"Total memes in DB: {Meme.query.count()}")

if __name__ == '__main__':
    seed_memes()
