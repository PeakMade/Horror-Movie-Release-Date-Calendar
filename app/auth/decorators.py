"""
Authentication decorators for protecting routes.
"""
from functools import wraps
from flask import session, redirect, url_for, request
import logging

logger = logging.getLogger(__name__)


def login_required(f):
    """
    Decorator to require authentication for a route.
    Redirects to login if user is not authenticated.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'access_token' not in session:
            logger.warning(f"Unauthenticated access attempt to {request.path}")
            # Store the original URL to redirect back after login
            session['next_url'] = request.url
            return redirect(url_for('auth_bp.login'))
        return f(*args, **kwargs)
    return decorated_function
