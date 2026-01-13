# Quick Reference - Authentication System

## 🚀 Quick Start (3 Steps)

1. **Get Azure AD credentials** → [SETUP_GUIDE.md](SETUP_GUIDE.md)
2. **Create `.env` file** → Copy from `.env.example` and fill in values
3. **Run app** → `pip install -r requirements.txt` then `python app.py`

---

## 📝 Common Code Patterns

### Protect a Route
```python
from app.auth.decorators import login_required
from app.auth.token_utils import ensure_fresh_access_token

@app.route('/protected')
@login_required
def my_route():
    ensure_fresh_access_token()  # Refresh token if needed
    # Your code here
```

### Get User Info
```python
from flask import session

user_name = session.get('user_name')
user_email = session.get('user_email')
```

### Make API Call
```python
from flask import session
import requests

access_token = session.get('access_token')
headers = {'Authorization': f'Bearer {access_token}'}
response = requests.get('https://graph.microsoft.com/v1.0/me', headers=headers)
```

### Check Authentication Status
```python
from flask import session

if 'access_token' in session:
    # User is authenticated
else:
    # User is not authenticated
```

---

## 🔧 Key Functions

| Function | Purpose | When to Use |
|----------|---------|-------------|
| `@login_required` | Protect route | Add to routes requiring authentication |
| `ensure_fresh_access_token()` | Refresh token | Call before API operations |
| `session.get('access_token')` | Get token | Use in API calls |
| `session.get('user_email')` | Get user email | Display user info |

---

## 🌐 Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/auth/login` | GET | Initiate OAuth login |
| `/auth/redirect` | GET | OAuth callback (set in Azure AD) |
| `/auth/logout` | GET | Clear session |
| `/auth/ping` | GET | Keep-alive (called by JavaScript) |

---

## 📂 Important Files

| File | Purpose |
|------|---------|
| `.env` | Environment variables (create from `.env.example`) |
| `app/auth/config.py` | OAuth configuration |
| `app/auth/token_utils.py` | Token refresh logic |
| `app/auth/decorators.py` | `@login_required` decorator |
| `app/routes/auth_routes.py` | Authentication endpoints |
| `templates/calendar.html` | Keep-alive JavaScript |

---

## ⚙️ Environment Variables

**Required in `.env` file:**

```env
CLIENT_ID=...              # From Azure AD app registration
TENANT_ID=...              # From Azure AD app registration
O365_CLIENT_SECRET=...     # From Azure AD app registration
REDIRECT_URI=http://localhost:5000/auth/redirect
SECRET_KEY=...             # Generate: python -c "import secrets; print(secrets.token_urlsafe(32))"
```

---

## 🔍 Troubleshooting

| Problem | Solution |
|---------|----------|
| "Missing environment variables" | Create `.env` file from `.env.example` |
| "CSRF state mismatch" | Clear cookies, check SECRET_KEY |
| "Token refresh failed" | Refresh token expired, re-login required |
| Keep-alive not working | Check browser console, verify `/auth/ping` works |

---

## 📚 Full Documentation

- **[AUTHENTICATION_GUIDE.md](AUTHENTICATION_GUIDE.md)** - Complete architecture guide
- **[SETUP_GUIDE.md](SETUP_GUIDE.md)** - Azure AD setup instructions
- **[IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md)** - Overview & quick start
- **[CHECKLIST.md](CHECKLIST.md)** - Implementation checklist
- **[example_usage.py](app/routes/example_usage.py)** - Code examples

---

## ⏱️ Token Lifecycle

```
Access Token:  1 hour → Auto-refresh at 55 min → New token
Refresh Token: 90 days → Rolling refresh → New refresh token
Session:       8 hours → Sliding window → Extends on activity
```

---

## 🔒 Security Features

✅ OAuth 2.0 Authorization Code Flow  
✅ CSRF protection (state token)  
✅ HTTP-only, Secure cookies  
✅ Tokens stored server-side only  
✅ Automatic token refresh  
✅ Session timeout (8 hours)  

---

## 🎯 Next Steps

1. ✅ Implementation complete
2. ⏳ Set up Azure AD app registration → [SETUP_GUIDE.md](SETUP_GUIDE.md#step-1-azure-ad-app-registration)
3. ⏳ Create `.env` file with credentials
4. ⏳ Test locally: `python app.py`
5. ⏳ Deploy to Azure (optional) → [SETUP_GUIDE.md](SETUP_GUIDE.md#step-4-azure-deployment-production)

---

**Need Help?** See [SETUP_GUIDE.md](SETUP_GUIDE.md#troubleshooting)
