import requests
from app import create_app
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

        existing_urls = {m.url for m in Meme.query.all()}
        memes_to_add = []

        # Try to fetch enough to fill up to 100
        attempts = 0
        while len(existing_urls) + len(memes_to_add) < 100 and attempts < 10:
            attempts += 1
            needed = 100 - (len(existing_urls) + len(memes_to_add))
            # fetch a bit more than needed to account for dupes
            fetch_count = min(50, needed + 10)

            try:
                print(f"Attempt {attempts}: Fetching {fetch_count} memes...")
                response = requests.get(f'https://meme-api.com/gimme/{fetch_count}')
                if response.status_code == 200:
                    data = response.json()
                    for meme_data in data.get('memes', []):
                        if len(existing_urls) + len(memes_to_add) >= 100:
                            break

                        url = meme_data.get('url')
                        if url and url not in existing_urls:
                            existing_urls.add(url) # prevent dupes in this batch
                            new_meme = Meme(
                                url=url,
                                title=meme_data.get('title', 'Untitled')
                            )
                            memes_to_add.append(new_meme)
            except Exception as e:
                print(f"Error fetching memes: {e}")

        # Add to DB
        if memes_to_add:
            for meme in memes_to_add:
                db.session.add(meme)
            db.session.commit()
            print(f"Successfully added {len(memes_to_add)} new memes.")
        else:
            print("No new memes added.")

        print(f"Total memes in DB: {Meme.query.count()}")

if __name__ == '__main__':
    seed_memes()
