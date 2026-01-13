"""
Authentication routes for OAuth login, callback, and logout.
"""
import logging
import secrets
from datetime import datetime, timedelta, timezone as tz
from flask import Blueprint, request, redirect, url_for, session, jsonify, flash
import msal
from app.auth.config import CLIENT_ID, CLIENT_SECRET, AUTHORITY, REDIRECT_URI, SCOPES, SP_SITE_URL, SP_LOG_LIST_ID
from app.auth.token_utils import get_msal_app, ensure_fresh_access_token
from app.services.sharepoint_service import log_login_activity

logger = logging.getLogger(__name__)

# Create blueprint
auth_bp = Blueprint('auth_bp', __name__, url_prefix='/auth')


@auth_bp.route('/login')
def login():
    """
    Initiate OAuth login flow.
    Redirects user to Microsoft login page.
    """
    from app.auth.config import CLIENT_ID, TENANT_ID, CLIENT_SECRET
    
    # Check if OAuth is properly configured
    if not CLIENT_ID or CLIENT_ID == 'placeholder-client-id' or \
       not TENANT_ID or TENANT_ID == 'placeholder-tenant-id' or \
       not CLIENT_SECRET or CLIENT_SECRET == 'placeholder-client-secret':
        flash('OAuth authentication is not configured. Please set up Azure AD credentials in .env file. See SETUP_GUIDE.md for instructions.', 'error')
        logger.warning("Login attempted but OAuth not configured")
        return redirect(url_for('select_year'))
    
    # Clear any existing session data
    session.clear()
    
    # Generate CSRF state token
    state = secrets.token_urlsafe(32)
    session["oauth_state"] = state
    
    try:
        # Get MSAL app
        msal_app = get_msal_app()
        
        # Build authorization URL
        auth_url = msal_app.get_authorization_request_url(
            scopes=SCOPES,
            redirect_uri=REDIRECT_URI,
            state=state,
            prompt="select_account"  # Force account selection
        )
        
        logger.info("Redirecting to Microsoft login")
        return redirect(auth_url)
    except Exception as e:
        logger.error(f"Failed to initiate OAuth login: {e}")
        flash('Authentication system is not properly configured. Please check your Azure AD settings.', 'error')
        return redirect(url_for('select_year'))


@auth_bp.route('/redirect')
def auth_redirect():
    """
    OAuth callback endpoint.
    Handles the redirect from Microsoft after user authentication.
    """
    # Validate CSRF state token
    if request.args.get('state') != session.get('oauth_state'):
        logger.error("CSRF state mismatch")
        flash('Invalid state parameter. Please try logging in again.', 'error')
        return redirect(url_for('select_year'))
    
    # Check for errors from Microsoft
    if 'error' in request.args:
        error = request.args.get('error')
        error_description = request.args.get('error_description', 'No description')
        logger.error(f"OAuth error: {error} - {error_description}")
        flash(f'Authentication error: {error_description}', 'error')
        return redirect(url_for('select_year'))
    
    # Get authorization code
    code = request.args.get('code')
    if not code:
        logger.error("No authorization code received")
        flash('No authorization code received. Please try again.', 'error')
        return redirect(url_for('select_year'))
    
    # Exchange authorization code for tokens
    msal_app = get_msal_app()
    
    try:
        result = msal_app.acquire_token_by_authorization_code(
            code,
            scopes=SCOPES,
            redirect_uri=REDIRECT_URI
        )
        
        if "access_token" in result:
            # Calculate token expiration time
            expires_in = result.get('expires_in', 3599)
            token_expires_at = datetime.now(tz.utc) + timedelta(seconds=expires_in)
            
            # Store tokens and expiration in session
            session['access_token'] = result['access_token']
            session['refresh_token'] = result.get('refresh_token')
            session['token_expires_at'] = token_expires_at.isoformat()
            
            # Get user information from Microsoft Graph
            try:
                import requests
                headers = {'Authorization': f"Bearer {result['access_token']}"}
                graph_response = requests.get(
                    'https://graph.microsoft.com/v1.0/me',
                    headers=headers,
                    timeout=10
                )
                
                if graph_response.status_code == 200:
                    user_info = graph_response.json()
                    session['user_name'] = user_info.get('displayName', 'User')
                    session['user_email'] = user_info.get('mail') or user_info.get('userPrincipalName')
                    logger.info(f"User logged in: {session['user_email']}")
                    
                    # Log login activity to SharePoint
                    if SP_SITE_URL and SP_LOG_LIST_ID:
                        try:
                            log_success = log_login_activity(
                                access_token=result['access_token'],
                                site_url=SP_SITE_URL,
                                list_id=SP_LOG_LIST_ID,
                                user_email=session['user_email'],
                                user_name=session['user_name'],
                                user_role=session.get('user_role', 'User')
                            )
                            if log_success:
                                logger.info(f"Login activity logged for {session['user_email']}")
                            else:
                                logger.warning(f"Failed to log login activity for {session['user_email']}")
                        except Exception as log_error:
                            logger.error(f"Exception logging login activity: {log_error}")
                    else:
                        logger.warning("SharePoint logging not configured (missing SP_SITE_URL or SP_LOG_LIST_ID)")
                    
                else:
                    logger.warning(f"Failed to fetch user info: {graph_response.status_code}")
                    session['user_name'] = 'User'
                    
            except Exception as e:
                logger.error(f"Error fetching user info: {e}")
                session['user_name'] = 'User'
            
            flash('Successfully logged in!', 'success')
            
            # Redirect to original URL or home page
            next_url = session.pop('next_url', None)
            return redirect(next_url or url_for('select_year'))
            
        else:
            # Token acquisition failed
            error = result.get('error', 'unknown_error')
            error_description = result.get('error_description', 'No description')
            logger.error(f"Token acquisition failed: {error} - {error_description}")
            flash(f'Failed to acquire token: {error_description}', 'error')
            return redirect(url_for('select_year'))
            
    except Exception as e:
        logger.error(f"Exception during token acquisition: {e}")
        flash('An error occurred during authentication. Please try again.', 'error')
        return redirect(url_for('select_year'))


@auth_bp.route('/logout')
def logout():
    """
    Log out the user by clearing the session.
    """
    user_email = session.get('user_email', 'Unknown user')
    session.clear()
    logger.info(f"User logged out: {user_email}")
    
    flash('Successfully logged out.', 'info')
    return redirect(url_for('select_year'))


@auth_bp.route('/ping')
def ping():
    """
    Keep-alive endpoint to maintain session and refresh tokens.
    Called periodically by JavaScript to keep the user logged in.
    """
    if 'access_token' not in session:
        logger.warning("Ping received without active session")
        return jsonify({'status': 'unauthorized'}), 401
    
    # Attempt to refresh token if needed
    try:
        if ensure_fresh_access_token():
            return jsonify({'status': 'ok'}), 200
        else:
            logger.warning("Token refresh failed in ping")
            return jsonify({'status': 'unauthorized'}), 401
    except Exception as e:
        logger.error(f"Error in ping endpoint: {e}")
        return jsonify({'status': 'error'}), 500
