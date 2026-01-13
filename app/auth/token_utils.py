"""
Token utility functions for OAuth token management and refresh.
"""
import logging
from datetime import datetime, timedelta, timezone as tz
from flask import session
import msal
from app.auth.config import CLIENT_ID, CLIENT_SECRET, AUTHORITY, SCOPES

logger = logging.getLogger(__name__)


def get_msal_app():
    """Create and return an MSAL confidential client application."""
    return msal.ConfidentialClientApplication(
        CLIENT_ID,
        authority=AUTHORITY,
        client_credential=CLIENT_SECRET
    )


def token_expiring_soon(skew_seconds=300):
    """
    Check if the access token is expiring within the specified time window.
    
    Args:
        skew_seconds (int): Time buffer in seconds (default 5 minutes)
        
    Returns:
        bool: True if token expires within the time window, False otherwise
    """
    token_expires_at_str = session.get('token_expires_at')
    
    if not token_expires_at_str:
        logger.warning("No token expiration time in session")
        return True
    
    try:
        token_expires_at = datetime.fromisoformat(token_expires_at_str)
        time_until_expiry = token_expires_at - datetime.now(tz.utc)
        seconds_until_expiry = time_until_expiry.total_seconds()
        
        logger.debug(f"Token expires in {seconds_until_expiry / 60:.1f} minutes")
        return seconds_until_expiry < skew_seconds
    except (ValueError, TypeError) as e:
        logger.error(f"Error parsing token expiration time: {e}")
        return True


def refresh_access_token():
    """
    Refresh the access token using the refresh token.
    
    Returns:
        bool: True if refresh successful, False otherwise
        
    Raises:
        AuthRequired: If refresh token is invalid or expired
    """
    refresh_token = session.get('refresh_token')
    
    if not refresh_token:
        logger.warning("No refresh token in session")
        return False
    
    try:
        msal_app = get_msal_app()
        
        # Use MSAL to refresh the token
        result = msal_app.acquire_token_by_refresh_token(
            refresh_token,
            scopes=SCOPES
        )
        
        if "access_token" in result:
            # Calculate new expiration time
            expires_in = result.get('expires_in', 3599)
            token_expires_at = datetime.now(tz.utc) + timedelta(seconds=expires_in)
            
            # Update session with new tokens
            session['access_token'] = result['access_token']
            session['token_expires_at'] = token_expires_at.isoformat()
            
            # Update refresh token if a new one was issued (rolling refresh)
            if 'refresh_token' in result:
                session['refresh_token'] = result['refresh_token']
            
            logger.info("Access token refreshed successfully")
            return True
        else:
            # Token refresh failed
            error = result.get('error', 'unknown_error')
            error_description = result.get('error_description', 'No description')
            logger.error(f"Token refresh failed: {error} - {error_description}")
            
            # Check for specific errors indicating re-authentication needed
            if error in ['invalid_grant', 'interaction_required']:
                logger.warning("Refresh token expired or invalid, re-authentication required")
            
            return False
            
    except Exception as e:
        logger.error(f"Exception during token refresh: {e}")
        return False


def ensure_fresh_access_token():
    """
    Ensure the access token is fresh (not expiring soon).
    If the token is expiring soon, attempt to refresh it.
    
    Returns:
        bool: True if token is fresh or was refreshed successfully
        
    Raises:
        AuthRequired: If re-authentication is required
    """
    if not session.get('access_token'):
        logger.warning("No access token in session")
        return False
    
    if token_expiring_soon():
        logger.info("Token expiring soon, attempting refresh...")
        if not refresh_access_token():
            logger.error("Token refresh failed, re-authentication required")
            return False
    
    return True


class AuthRequired(Exception):
    """Exception raised when authentication is required."""
    pass
