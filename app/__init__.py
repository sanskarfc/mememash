from flask import Flask
from flask_apscheduler import APScheduler
from .models import db, User

scheduler = APScheduler()

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'dev-secret-key-change-this-in-prod'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///mememash.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Scheduler Config
    app.config['SCHEDULER_API_ENABLED'] = True

    db.init_app(app)

    # Initialize Scheduler
    scheduler.init_app(app)

    from .tasks import fetch_and_store_memes

    # Add scheduled job
    @scheduler.task('interval', id='fetch_memes_job', hours=1)
    def scheduled_fetch_memes():
        with app.app_context():
            fetch_and_store_memes()

    scheduler.start()

    from flask_login import LoginManager
    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(id):
        return db.session.get(User, int(id))

    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint)

    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    return app
