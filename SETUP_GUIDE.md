# OAuth Authentication Setup Guide

This guide explains how to set up OAuth authentication for the Calendar App using Microsoft Entra ID (Azure AD).

## Prerequisites

- Microsoft Azure account with admin access
- Python 3.8+ installed
- Git installed (optional)

## Step 1: Azure AD App Registration

### 1.1 Create App Registration

1. Go to [Azure Portal](https://portal.azure.com)
2. Navigate to **Azure Active Directory** → **App registrations**
3. Click **New registration**
4. Fill in the details:
   - **Name**: Calendar App (or your preferred name)
   - **Supported account types**: Accounts in this organizational directory only
   - **Redirect URI**: 
     - Platform: Web
     - URL: `http://localhost:5000/auth/redirect` (for local development)

5. Click **Register**

### 1.2 Note Your App IDs

After registration, note the following from the **Overview** page:
- **Application (client) ID** - This is your `CLIENT_ID`
- **Directory (tenant) ID** - This is your `TENANT_ID`

### 1.3 Create Client Secret

1. In your app registration, go to **Certificates & secrets**
2. Click **New client secret**
3. Add description: "Calendar App Secret"
4. Choose expiration: 24 months (recommended)
5. Click **Add**
6. **IMPORTANT**: Copy the **Value** immediately (this is your `O365_CLIENT_SECRET`)
   - You cannot view it again after leaving this page!

### 1.4 Configure API Permissions

1. Go to **API permissions**
2. Click **Add a permission**
3. Select **Microsoft Graph**
4. Choose **Delegated permissions**
5. Add the following permissions:
   - `User.Read` - Read user profile
   - `Files.ReadWrite.All` - Read and write files (if needed for future features)
   - `Sites.ReadWrite.All` - Read and write SharePoint sites (if needed)
6. Click **Add permissions**
7. Click **Grant admin consent** (if you have admin rights)

### 1.5 Add Redirect URIs

1. Go to **Authentication**
2. Under **Platform configurations** → **Web**
3. Add redirect URIs:
   - Local: `http://localhost:5000/auth/redirect`
   - Production: `https://your-app.azurewebsites.net/auth/redirect`
4. Under **Implicit grant and hybrid flows**: Leave unchecked (we use authorization code flow)
5. Save changes

## Step 2: Local Development Setup

### 2.1 Clone or Download the Project

```bash
cd "c:\Users\pbatson\Desktop\Project Folder\Calendar App test"
```

### 2.2 Create Virtual Environment (Recommended)

```bash
python -m venv venv
venv\Scripts\activate
```

### 2.3 Install Dependencies

```bash
pip install -r requirements.txt
```

### 2.4 Create Environment File

1. Copy the example file:
   ```bash
   copy .env.example .env
   ```

2. Edit `.env` with your values:
   ```env
   # OAuth Configuration
   CLIENT_ID=your-application-client-id-from-azure
   TENANT_ID=your-directory-tenant-id-from-azure
   O365_CLIENT_SECRET=your-client-secret-value-from-azure
   REDIRECT_URI=http://localhost:5000/auth/redirect

   # Flask Configuration
   SECRET_KEY=generate-a-random-secret-key-here

   # OMDb API Configuration
   OMDB_API_KEY=4aecb6ba
   OMDB_BASE_URL=http://www.omdbapi.com/

   # Environment
   FLASK_ENV=development
   FLASK_DEBUG=True
   ```

### 2.5 Generate Secret Key

Generate a secure secret key using Python:

```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

Copy the output and use it as your `SECRET_KEY` in `.env`

### 2.6 Run the Application

```bash
python app.py
```

The application will start at `http://localhost:5000`

## Step 3: Testing Authentication

1. Open browser and go to `http://localhost:5000`
2. Click **Login** in the top right
3. You'll be redirected to Microsoft login
4. Sign in with your Microsoft account
5. Grant permissions (first time only)
6. You'll be redirected back to the app

## Step 4: Azure Deployment (Production)

### 4.1 Update Azure App Registration

1. In Azure Portal → **App registrations** → Your app
2. Go to **Authentication**
3. Add production redirect URI:
   ```
   https://your-app.azurewebsites.net/auth/redirect
   ```

### 4.2 Configure Azure App Service

1. Go to **App Service** → Your app
2. Navigate to **Configuration** → **Application settings**
3. Add the following settings:

   ```
   CLIENT_ID=your-client-id
   TENANT_ID=your-tenant-id
   O365_CLIENT_SECRET=your-client-secret
   REDIRECT_URI=https://your-app.azurewebsites.net/auth/redirect
   SECRET_KEY=your-generated-secret-key
   FLASK_ENV=production
   FLASK_DEBUG=False
   OMDB_API_KEY=4aecb6ba
   OMDB_BASE_URL=http://www.omdbapi.com/
   ```

4. Save changes

### 4.3 Enable ARR Affinity (Important!)

1. In App Service → **Configuration** → **General settings**
2. Set **ARR affinity**: **ON**
3. Save changes

This is required for multi-instance deployments to ensure session persistence.

### 4.4 Deploy Application

Use Azure CLI, VS Code, GitHub Actions, or your preferred deployment method.

## Architecture Overview

### Authentication Flow

1. User clicks **Login**
2. Redirected to Microsoft login page
3. User authenticates (with MFA if enabled)
4. Microsoft redirects back with authorization code
5. App exchanges code for access token and refresh token
6. Tokens stored in server-side session (filesystem)
7. User can access protected resources

### Token Refresh

- Access tokens expire after 1 hour
- Before expiration (5-minute buffer), tokens are automatically refreshed
- Refresh tokens are used to obtain new access tokens
- Refresh tokens are rolling (new one issued with each refresh)

### Keep-Alive Mechanism

- JavaScript pings server every 10 minutes (if user active)
- Keeps session alive and refreshes tokens proactively
- Session expires after 8 hours of inactivity

### Session Management

- Sessions stored in filesystem (`./flask_session/` or `/home/flask_session/`)
- Session ID stored in HTTP-only cookie (secure)
- Tokens never exposed to browser
- Old sessions cleaned up on app startup (>9 hours old)

## Security Best Practices

### 1. Never Commit Secrets
```bash
# Ensure .env is in .gitignore
echo .env >> .gitignore
```

### 2. Rotate Client Secrets Regularly
- Client secrets expire after 24 months
- Set calendar reminder to rotate before expiration

### 3. Use Strong Secret Keys
- Always use cryptographically random secret keys
- Never reuse secret keys across applications

### 4. Enable HTTPS in Production
- Azure App Service automatically provides HTTPS
- Session cookies are marked as Secure in production

### 5. Monitor Token Usage
- Check application logs for token refresh failures
- Monitor for unusual authentication patterns

## Troubleshooting

### "Missing required environment variables"
- Ensure `.env` file exists and contains all required variables
- Check that variable names match exactly

### "CSRF state mismatch"
- Clear browser cookies and try again
- Check that `SECRET_KEY` is set correctly

### "Token refresh failed"
- Refresh token may have expired
- User needs to log in again
- Check Azure AD token lifetime policies

### "Session not found"
- Clear browser cookies
- Check that `flask_session/` directory exists and is writable
- Verify ARR affinity is enabled in Azure

### "Invalid client secret"
- Verify `O365_CLIENT_SECRET` matches the value from Azure Portal
- Client secret may have expired (check in Azure Portal)

## Additional Resources

- [MSAL Python Documentation](https://msal-python.readthedocs.io/)
- [Microsoft Graph API](https://docs.microsoft.com/en-us/graph/)
- [Azure App Service Configuration](https://docs.microsoft.com/en-us/azure/app-service/)
- [Flask-Session Documentation](https://flask-session.readthedocs.io/)

## Support

For issues or questions, refer to the AUTHENTICATION_GUIDE.md for detailed implementation information.
