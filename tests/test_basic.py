import unittest
from app import create_app
from app.models import db, User, Meme

class MememashTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.app.config['WTF_CSRF_ENABLED'] = False
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'

        self.client = self.app.test_client()

        with self.app.app_context():
            db.create_all()

            # Create test user
            u = User(username='testuser')
            u.set_password('testpass')
            db.session.add(u)

            # Create test memes
            m1 = Meme(url='http://example.com/1.jpg', title='Meme 1', elo_rating=1200)
            m2 = Meme(url='http://example.com/2.jpg', title='Meme 2', elo_rating=1200)
            db.session.add(m1)
            db.session.add(m2)
            db.session.commit()

    def tearDown(self):
        with self.app.app_context():
            db.session.remove()
            db.drop_all()

    def test_index_redirects_unauthorized(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 302)
        self.assertIn('/login', response.location)

    def test_login(self):
        response = self.client.post('/login', data=dict(
            username='testuser',
            password='testpass'
        ), follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Vote', response.data)

    def test_voting_logic(self):
        # Login first
        self.client.post('/login', data=dict(
            username='testuser',
            password='testpass'
        ), follow_redirects=True)

        with self.app.app_context():
            m1 = Meme.query.filter_by(title='Meme 1').first()
            m2 = Meme.query.filter_by(title='Meme 2').first()
            m1_id = m1.id
            m2_id = m2.id

        # Vote for m1 (winner) over m2 (loser)
        response = self.client.post('/vote', data=dict(
            winner_id=m1_id,
            loser_id=m2_id
        ), follow_redirects=True)

        self.assertEqual(response.status_code, 200)

        with self.app.app_context():
            m1 = db.session.get(Meme, m1_id)
            m2 = db.session.get(Meme, m2_id)

            # m1 should have > 1200, m2 < 1200
            self.assertTrue(m1.elo_rating > 1200)
            self.assertTrue(m2.elo_rating < 1200)
            self.assertEqual(m1.wins, 1)
            self.assertEqual(m2.losses, 1)

if __name__ == '__main__':
    unittest.main()
