from .auth import auth_bp
from .dashboard import dashboard_bp
from .events import events_bp
from .messages import messages_bp
from .calendar import calendar_bp
from .templates import templates_bp
from .errors import errors_bp

def register_blueprints(app):
    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(events_bp)
    app.register_blueprint(messages_bp)
    app.register_blueprint(calendar_bp)
    app.register_blueprint(templates_bp)
    app.register_blueprint(errors_bp)
