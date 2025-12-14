from flask import Blueprint, render_template, request, redirect, url_for
from flask_login import login_required, current_user
from .models import db, Meme
import random

main = Blueprint('main', __name__)

@main.route('/')
@login_required
def index():
    # Pick 2 random memes
    # Use func.random() if we want database-level randomness,
    # but for small dataset python random choice is fine and DB agnostic.
    all_memes = Meme.query.all()
    if len(all_memes) < 2:
        return "Not enough memes to play!", 500

    contestants = random.sample(all_memes, 2)
    return render_template('index.html', meme1=contestants[0], meme2=contestants[1])

@main.route('/vote', methods=['POST'])
@login_required
def vote():
    winner_id = request.form.get('winner_id')
    loser_id = request.form.get('loser_id')

    winner = db.session.get(Meme, int(winner_id))
    loser = db.session.get(Meme, int(loser_id))

    if winner and loser:
        update_elo(winner, loser)
        db.session.commit()

    return redirect(url_for('main.index'))

def update_elo(winner, loser, k=32):
    # Calculate Expected Scores
    expected_winner = 1 / (1 + 10 ** ((loser.elo_rating - winner.elo_rating) / 400))
    expected_loser = 1 / (1 + 10 ** ((winner.elo_rating - loser.elo_rating) / 400))

    # Update Ratings
    winner.elo_rating = winner.elo_rating + k * (1 - expected_winner)
    loser.elo_rating = loser.elo_rating + k * (0 - expected_loser)

    # Update stats
    winner.wins += 1
    loser.losses += 1

@main.route('/leaderboard')
@login_required
def leaderboard():
    # Top 50 memes
    top_memes = Meme.query.order_by(Meme.elo_rating.desc()).limit(50).all()
    return render_template('leaderboard.html', memes=top_memes)
