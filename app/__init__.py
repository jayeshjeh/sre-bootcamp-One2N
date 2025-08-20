from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from dotenv import load_dotenv
from sqlalchemy import text
import os

db = SQLAlchemy()
migrate = Migrate()

def create_app():
    load_dotenv()
    
    app = Flask(__name__)
    app.config.from_object("config.Config")

    db.init_app(app)
    migrate.init_app(app, db)

    from app.routes.student import student_bp
    app.register_blueprint(student_bp, url_prefix="/api/v1")

    from app.logger import setup_logging
    setup_logging(app)

    @app.before_request
    def start_timer():
        from flask import g
        import time
        g.start_time = time.time()

    @app.after_request
    def log_request(response):
        from flask import request, g
        import time
        duration = round((time.time() - g.start_time) * 1000)
        ip = request.headers.get("X-Forwarded-For", request.remote_addr)
        app.logger.info(f"{ip} {request.method} {request.path} {response.status_code} {duration}ms")
        return response

    @app.route("/healthcheck")
    def healthcheck():
        try:
            db.session.execute(text("SELECT 1"))
            return jsonify({"status": "ok", "database": "ok"}), 200
        except Exception as e:
            app.logger.error(f"Healthcheck failed: {e}")
            return jsonify({"status": "error", "database": "unreachable"}), 500

    return app
