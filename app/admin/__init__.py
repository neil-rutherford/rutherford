from flask import Blueprint

bp = Blueprint('admin', __name__)

from app.admin import article_routes, contact_routes, feedback_routes
