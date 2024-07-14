# Initialize Blueprint instances for each route
from flask import Blueprint

event_bp = Blueprint('event_bp', __name__)
user_bp = Blueprint('user_bp', __name__)
participant_bp = Blueprint('participant_bp', __name__)
auth_bp = Blueprint('auth_bp', __name__)
analytics_bp = Blueprint('anaytics_bp', __name__)

# Import routes to register with blueprints
from . import event_routes, user_routes, participant_routes, auth_routes
