"""
Configuration module for authentication.
"""
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# OAuth Configuration
CLIENT_ID = os.environ.get('CLIENT_ID') or os.environ.get('AZURE_CLIENT_ID')
TENANT_ID = os.environ.get('TENANT_ID') or os.environ.get('AZURE_TENANT_ID')
CLIENT_SECRET = os.environ.get('O365_CLIENT_SECRET') or os.environ.get('AZURE_CLIENT_SECRET')
REDIRECT_URI = os.environ.get('REDIRECT_URI', 'http://localhost:5000/auth/redirect')

# SharePoint Configuration
SP_SITE_URL = os.environ.get('SP_SITE_URL', 'https://peakcampus.sharepoint.com/sites/BaseCampApps')
SP_LOG_LIST_ID = os.environ.get('SP_LOG_LIST_ID')

# Microsoft authority URL
AUTHORITY = f"https://login.microsoftonline.com/{TENANT_ID}"

# OAuth scopes (offline_access is automatically added by MSAL)
SCOPES = ["User.Read", "Files.ReadWrite.All", "Sites.ReadWrite.All"]

# Validate required environment variables
def validate_config():
    """Validate that all required OAuth configuration variables are set."""
    missing = []
    if not CLIENT_ID:
        missing.append('CLIENT_ID or AZURE_CLIENT_ID')
    if not TENANT_ID:
        missing.append('TENANT_ID or AZURE_TENANT_ID')
    if not CLIENT_SECRET:
        missing.append('O365_CLIENT_SECRET or AZURE_CLIENT_SECRET')
    
    if missing:
        raise ValueError(f"Missing required environment variables: {', '.join(missing)}")

# Validate on import
try:
    validate_config()
except ValueError as e:
    print(f"Warning: {e}")
