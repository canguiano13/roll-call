from .auth import auth
from .home import home
from .events import events
from .messages import messages
from .errors import errors

def register_blueprints(app):
    app.register_blueprint(auth)
    app.register_blueprint(home)
    app.register_blueprint(events)
    app.register_blueprint(messages)
    app.register_blueprint(errors)
