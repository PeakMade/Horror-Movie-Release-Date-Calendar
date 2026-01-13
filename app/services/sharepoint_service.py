"""
SharePoint service for interacting with SharePoint lists via Microsoft Graph API.
"""
import logging
import requests
from datetime import datetime, timezone as tz
from flask import session

logger = logging.getLogger(__name__)


class SharePointService:
    """Service class for SharePoint operations via Microsoft Graph API."""
    
    def __init__(self, site_url, access_token):
        """
        Initialize SharePoint service.
        
        Args:
            site_url (str): SharePoint site URL (e.g., https://tenant.sharepoint.com/sites/sitename)
            access_token (str): Valid OAuth access token with Sites.ReadWrite.All permission
        """
        self.site_url = site_url
        self.access_token = access_token
        self.graph_base_url = "https://graph.microsoft.com/v1.0"
        
    def _get_site_id(self):
        """
        Get the SharePoint site ID from the site URL.
        
        Returns:
            str: Site ID or None if not found
        """
        # Extract hostname and site path from URL
        # Example: https://tenant.sharepoint.com/sites/sitename
        # Hostname: tenant.sharepoint.com
        # Site path: /sites/sitename
        
        from urllib.parse import urlparse
        parsed = urlparse(self.site_url)
        hostname = parsed.netloc
        site_path = parsed.path
        
        # Graph API endpoint to get site by hostname and path
        endpoint = f"{self.graph_base_url}/sites/{hostname}:{site_path}"
        
        headers = {
            'Authorization': f'Bearer {self.access_token}',
            'Accept': 'application/json'
        }
        
        try:
            response = requests.get(endpoint, headers=headers, timeout=10)
            
            if response.status_code == 200:
                site_data = response.json()
                site_id = site_data.get('id')
                logger.info(f"Retrieved site ID: {site_id}")
                return site_id
            else:
                logger.error(f"Failed to get site ID: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"Exception getting site ID: {e}")
            return None
    
    def add_list_item(self, list_id, item_data):
        """
        Add an item to a SharePoint list.
        
        Args:
            list_id (str): The GUID of the SharePoint list
            item_data (dict): Dictionary of field names and values
            
        Returns:
            dict: Response data or None if failed
        """
        # Get site ID
        site_id = self._get_site_id()
        if not site_id:
            logger.error("Could not get site ID")
            return None
        
        # Build the endpoint URL
        endpoint = f"{self.graph_base_url}/sites/{site_id}/lists/{list_id}/items"
        
        headers = {
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        
        # Prepare the request body
        # Graph API expects fields in a 'fields' object
        body = {
            'fields': item_data
        }
        
        try:
            response = requests.post(endpoint, headers=headers, json=body, timeout=10)
            
            if response.status_code in [200, 201]:
                logger.info(f"Successfully added item to list {list_id}")
                return response.json()
            else:
                logger.error(f"Failed to add list item: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"Exception adding list item: {e}")
            return None
    
    def log_user_activity(self, list_id, user_email, user_name, activity_type, application="Calendar App", user_role="User"):
        """
        Log user activity to SharePoint list.
        
        Args:
            list_id (str): The GUID of the activity log list
            user_email (str): User's email address
            user_name (str): User's display name
            activity_type (str): Type of activity (e.g., "Login", "Logout", "View", "Edit")
            application (str): Application name (default: "Calendar App")
            user_role (str): User's role (default: "User")
            
        Returns:
            bool: True if successful, False otherwise
        """
        # Prepare the item data
        item_data = {
            'Title': f"{user_name} - {activity_type}",
            'UserEmail': user_email,
            'UserName': user_name,
            'LoginTimestamp': datetime.now(tz.utc).isoformat(),
            'UserRole': user_role,
            'ActivityType': activity_type,
            'Application': application
        }
        
        logger.info(f"Logging activity: {activity_type} for user {user_email}")
        
        result = self.add_list_item(list_id, item_data)
        
        return result is not None


def log_login_activity(access_token, site_url, list_id, user_email, user_name, user_role="User"):
    """
    Helper function to log user login activity to SharePoint.
    
    Args:
        access_token (str): Valid OAuth access token
        site_url (str): SharePoint site URL
        list_id (str): Activity log list ID
        user_email (str): User's email
        user_name (str): User's display name
        user_role (str): User's role (default: "User")
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        sp_service = SharePointService(site_url, access_token)
        return sp_service.log_user_activity(
            list_id=list_id,
            user_email=user_email,
            user_name=user_name,
            activity_type="Login",
            application="Horror Movie Calendar",
            user_role=user_role
        )
    except Exception as e:
        logger.error(f"Failed to log login activity: {e}")
        return False
