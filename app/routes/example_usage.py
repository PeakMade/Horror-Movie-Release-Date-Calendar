"""
Example: How to Use Authentication in Your Routes

This file demonstrates various patterns for using the authentication system
in your Flask application.
"""

from flask import Blueprint, session, jsonify, render_template
from app.auth.decorators import login_required
from app.auth.token_utils import ensure_fresh_access_token
import requests

# Example blueprint
example_bp = Blueprint('example_bp', __name__)


# ============================================================================
# PATTERN 1: Public Route (No Authentication Required)
# ============================================================================

@example_bp.route('/public')
def public_route():
    """
    A public route that anyone can access without authentication.
    """
    return render_template('public_page.html')


# ============================================================================
# PATTERN 2: Protected Route (Authentication Required)
# ============================================================================

@example_bp.route('/protected')
@login_required
def protected_route():
    """
    A protected route that requires authentication.
    Redirects to login if user is not authenticated.
    """
    # Access user information from session
    user_name = session.get('user_name', 'User')
    user_email = session.get('user_email', 'unknown@example.com')
    
    return render_template('protected_page.html', 
                         user_name=user_name, 
                         user_email=user_email)


# ============================================================================
# PATTERN 3: Protected Route with API Call
# ============================================================================

@example_bp.route('/api/data')
@login_required
def api_data():
    """
    A protected route that makes API calls using the access token.
    Automatically refreshes token before making API calls.
    """
    # Ensure token is fresh (refreshes if <5 minutes remaining)
    if not ensure_fresh_access_token():
        return jsonify({'error': 'Authentication required'}), 401
    
    # Get access token from session
    access_token = session.get('access_token')
    
    # Example: Call Microsoft Graph API
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }
    
    try:
        response = requests.get(
            'https://graph.microsoft.com/v1.0/me',
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 200:
            user_data = response.json()
            return jsonify({
                'status': 'success',
                'data': user_data
            })
        else:
            return jsonify({
                'status': 'error',
                'message': 'API call failed'
            }), response.status_code
            
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


# ============================================================================
# PATTERN 4: Optional Authentication
# ============================================================================

@example_bp.route('/optional-auth')
def optional_auth_route():
    """
    A route that works with or without authentication.
    Shows different content based on authentication status.
    """
    is_authenticated = 'access_token' in session
    
    if is_authenticated:
        user_name = session.get('user_name', 'User')
        return render_template('page.html', 
                             authenticated=True, 
                             user_name=user_name)
    else:
        return render_template('page.html', 
                             authenticated=False)


# ============================================================================
# PATTERN 5: POST Route with Form Data
# ============================================================================

@example_bp.route('/submit', methods=['POST'])
@login_required
def submit_form():
    """
    A protected POST route that handles form submissions.
    """
    # Ensure token is fresh before processing
    if not ensure_fresh_access_token():
        return jsonify({'error': 'Authentication required'}), 401
    
    # Get form data
    from flask import request
    form_data = request.form.get('data')
    
    # Process form data...
    # (Your logic here)
    
    return jsonify({
        'status': 'success',
        'message': 'Form submitted successfully'
    })


# ============================================================================
# PATTERN 6: JSON API Endpoint
# ============================================================================

@example_bp.route('/api/protected-data', methods=['GET'])
@login_required
def get_protected_data():
    """
    A protected JSON API endpoint.
    """
    # Ensure token is fresh
    if not ensure_fresh_access_token():
        return jsonify({'error': 'Authentication required'}), 401
    
    # Get user email from session
    user_email = session.get('user_email')
    
    # Return protected data
    return jsonify({
        'status': 'success',
        'data': {
            'user': user_email,
            'items': ['item1', 'item2', 'item3']
        }
    })


# ============================================================================
# PATTERN 7: SharePoint API Call
# ============================================================================

@example_bp.route('/sharepoint/files')
@login_required
def get_sharepoint_files():
    """
    A route that accesses SharePoint files via Microsoft Graph.
    """
    # Ensure token is fresh
    if not ensure_fresh_access_token():
        return jsonify({'error': 'Authentication required'}), 401
    
    access_token = session.get('access_token')
    
    # Example: Get SharePoint site
    site_url = 'https://yourtenant.sharepoint.com/sites/yoursite'
    
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Accept': 'application/json'
    }
    
    try:
        # Get site info
        graph_url = f"https://graph.microsoft.com/v1.0/sites/{site_url}"
        response = requests.get(graph_url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            site_data = response.json()
            return jsonify({
                'status': 'success',
                'site': site_data
            })
        else:
            return jsonify({
                'status': 'error',
                'message': 'Failed to access SharePoint'
            }), response.status_code
            
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def make_graph_api_call(endpoint, method='GET', data=None):
    """
    Helper function to make Microsoft Graph API calls with automatic
    token refresh.
    
    Args:
        endpoint (str): Graph API endpoint (e.g., '/me' or '/sites/...')
        method (str): HTTP method (GET, POST, etc.)
        data (dict): Optional data for POST/PATCH requests
        
    Returns:
        dict: JSON response from API or error dict
    """
    # Ensure token is fresh
    if not ensure_fresh_access_token():
        return {'error': 'Authentication required'}
    
    access_token = session.get('access_token')
    
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }
    
    url = f'https://graph.microsoft.com/v1.0{endpoint}'
    
    try:
        if method == 'GET':
            response = requests.get(url, headers=headers, timeout=10)
        elif method == 'POST':
            response = requests.post(url, headers=headers, json=data, timeout=10)
        elif method == 'PATCH':
            response = requests.patch(url, headers=headers, json=data, timeout=10)
        else:
            return {'error': f'Unsupported method: {method}'}
        
        if response.status_code in [200, 201, 204]:
            return response.json() if response.content else {'status': 'success'}
        else:
            return {
                'error': f'API call failed with status {response.status_code}',
                'details': response.text
            }
            
    except Exception as e:
        return {'error': str(e)}


# ============================================================================
# USAGE EXAMPLES IN YOUR app.py
# ============================================================================

"""
To use these patterns in your app.py:

1. Import the decorator and token utilities:
   
   from app.auth.decorators import login_required
   from app.auth.token_utils import ensure_fresh_access_token

2. Protect your routes:

   @app.route('/calendar', methods=['POST'])
   @login_required
   def display_calendar():
       ensure_fresh_access_token()
       # ... your existing code ...

3. Access user information:

   user_name = session.get('user_name')
   user_email = session.get('user_email')

4. Make API calls:

   access_token = session.get('access_token')
   headers = {'Authorization': f'Bearer {access_token}'}
   response = requests.get('https://api.example.com/data', headers=headers)

5. Check authentication status:

   if 'access_token' in session:
       # User is authenticated
   else:
       # User is not authenticated
"""
