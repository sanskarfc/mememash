import requests
from app.models import db, Meme

def fetch_and_store_memes(limit=50):
    """
    Fetches memes from the API and stores new unique ones in the database.
    """
    existing_urls = {m.url for m in Meme.query.all()}
    memes_to_add = []

    try:
        # Fetch a batch
        # We request 'limit' amount. The API might return dupes, so we filter.
        response = requests.get(f'https://meme-api.com/gimme/{limit}')
        if response.status_code == 200:
            data = response.json()
            for meme_data in data.get('memes', []):
                url = meme_data.get('url')
                if url and url not in existing_urls:
                    existing_urls.add(url)
                    new_meme = Meme(
                        url=url,
                        title=meme_data.get('title', 'Untitled')
                    )
                    memes_to_add.append(new_meme)

        if memes_to_add:
            for meme in memes_to_add:
                db.session.add(meme)
            db.session.commit()
            print(f"Scheduled Task: Added {len(memes_to_add)} new memes.")
        else:
            print("Scheduled Task: No new unique memes found in this batch.")

    except Exception as e:
        print(f"Scheduled Task Error: {e}")
