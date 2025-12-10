# Deploying HAI Facilities Dashboard to Streamlit Community Cloud

## Table of Contents
1. [Overview](#overview)
2. [Prerequisites](#prerequisites)
3. [Step 1: Prepare Your GitHub Repository](#step-1-prepare-your-github-repository)
4. [Step 2: Prepare BigQuery Service Account](#step-2-prepare-bigquery-service-account)
5. [Step 3: Create Streamlit Community Cloud Account](#step-3-create-streamlit-community-cloud-account)
6. [Step 4: Deploy Your Application](#step-4-deploy-your-application)
7. [Step 5: Configure Secrets (Critical)](#step-5-configure-secrets-critical)
8. [Step 6: Advanced Configuration](#step-6-advanced-configuration)
9. [Step 7: Testing & Verification](#step-7-testing--verification)
10. [Step 8: Troubleshooting](#step-8-troubleshooting)
11. [Maintenance & Updates](#maintenance--updates)
12. [Appendices](#appendices)

---

## Overview

This guide provides step-by-step instructions for deploying the **HAI Facilities Data Dashboard** Streamlit application to Streamlit Community Cloud. The application connects to Google BigQuery, so proper authentication and secrets management are critical for successful deployment.

**What is Streamlit Community Cloud?**
- Free hosting platform for Streamlit applications
- Integrated with GitHub for automatic deployments
- Built-in secrets management
- Supports Python dependencies via requirements.txt
- Provides HTTPS by default

**Estimated Time to Complete:** 30-45 minutes

**Cost:** Free (Streamlit Community Cloud free tier)

---

## Prerequisites

Before starting, ensure you have:

### Required Accounts
- ✅ **GitHub Account** - [Sign up here](https://github.com/signup)
- ✅ **Google Cloud Platform (GCP) Account** - [Sign up here](https://cloud.google.com/)
- ✅ **Access to BigQuery** - Project `hai-dev` with dataset `facilities`

### Required Permissions
- ✅ **GitHub:** Ability to create repositories
- ✅ **GCP:** Ability to create service accounts and download JSON keys
- ✅ **BigQuery:** Read access to tables in `hai-dev.facilities` dataset

### Local Setup
- ✅ Git installed on your machine
- ✅ Command line access (Terminal/Command Prompt)
- ✅ Code editor (VS Code, Sublime, etc.)

---

## Step 1: Prepare Your GitHub Repository

### 1.1 Initialize Git Repository (if not already done)

```bash
cd /Users/waqas/HAI_demo

# Initialize git repository
git init

# Verify .gitignore exists and is working
cat .gitignore
```

**Important:** Verify that `.gitignore` includes:
```
.env
credentials/
*.json
```

This prevents accidental commit of sensitive credentials.

### 1.2 Create GitHub Repository

**Option A: Via GitHub Website (Recommended)**

1. Go to [https://github.com/new](https://github.com/new)
2. Fill in repository details:
   - **Repository name:** `hai-facilities-dashboard` (or your preferred name)
   - **Description:** "Healthcare facilities data dashboard with BigQuery integration"
   - **Visibility:** Private (recommended) or Public
   - **Do NOT** initialize with README (you already have one)
3. Click "Create repository"

**Option B: Via GitHub CLI**

```bash
gh repo create hai-facilities-dashboard --private --source=. --remote=origin
```

### 1.3 Add Remote and Push Code

```bash
# Add GitHub remote (replace with your username)
git remote add origin https://github.com/YOUR_USERNAME/hai-facilities-dashboard.git

# Stage all files
git add .

# Create initial commit
git commit -m "Initial commit: HAI Facilities Dashboard with Phase 6"

# Push to GitHub
git branch -M main
git push -u origin main
```

### 1.4 Verify Repository Contents

Go to your GitHub repository URL and verify:
- ✅ `app.py` is present
- ✅ `config.py` is present
- ✅ `requirements.txt` is present
- ✅ `database/` and `utils/` directories exist
- ❌ `.env` file is NOT visible (should be ignored)
- ❌ `credentials/` directory is NOT visible (should be ignored)

---

## Step 2: Prepare BigQuery Service Account

### 2.1 Create Service Account

1. **Go to GCP Console:** [https://console.cloud.google.com](https://console.cloud.google.com)
2. **Select Project:** `hai-dev` (or your project)
3. **Navigate to:** IAM & Admin → Service Accounts
4. **Click:** "Create Service Account"
5. **Fill in details:**
   - **Service account name:** `streamlit-bigquery-reader`
   - **Service account ID:** `streamlit-bigquery-reader@hai-dev.iam.gserviceaccount.com`
   - **Description:** "Service account for Streamlit app to read BigQuery data"
6. **Click:** "Create and Continue"

### 2.2 Grant Permissions

In the "Grant this service account access to project" section:

**Required Role:** `BigQuery Data Viewer`
- This allows read access to datasets and tables

**Optional Role (if running queries):** `BigQuery Job User`
- This allows creating and running query jobs

Click "Continue" and then "Done"

### 2.3 Download JSON Key

1. **Find your service account** in the list
2. **Click the three dots** (⋮) on the right → "Manage keys"
3. **Click:** "Add Key" → "Create new key"
4. **Select:** JSON format
5. **Click:** "Create"
6. **Download location:** The JSON key will download to your computer

**⚠️ Security Warning:** This JSON file contains credentials. Keep it secure and never commit to GitHub!

### 2.4 Prepare JSON for Streamlit Secrets

Open the downloaded JSON file. It will look like this:

```json
{
  "type": "service_account",
  "project_id": "hai-dev",
  "private_key_id": "abc123...",
  "private_key": "-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n",
  "client_email": "streamlit-bigquery-reader@hai-dev.iam.gserviceaccount.com",
  "client_id": "123456789",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/..."
}
```

**Keep this file open** - you'll need it in Step 5.

---

## Step 3: Create Streamlit Community Cloud Account

### 3.1 Sign Up for Streamlit Community Cloud

1. **Go to:** [https://streamlit.io/cloud](https://streamlit.io/cloud)
2. **Click:** "Sign up" or "Get started"
3. **Sign in with GitHub:** Click "Continue with GitHub"
4. **Authorize Streamlit:** Grant Streamlit access to your GitHub account
5. **Complete profile:** Add your name and email if prompted

### 3.2 Verify Email (if required)

Check your email inbox and verify your email address if prompted.

### 3.3 Create Workspace

1. **Workspace name:** Personal (default) or create organization workspace
2. **Review terms:** Accept terms of service

You're now ready to deploy!

---

## Step 4: Deploy Your Application

### 4.1 Access Deployment Interface

1. **Go to:** [https://share.streamlit.io](https://share.streamlit.io)
2. **Click:** "New app" button (top right)

### 4.2 Configure Deployment Settings

Fill in the deployment form:

**Repository, Branch, and File Path:**
```
Repository: YOUR_USERNAME/hai-facilities-dashboard
Branch: main
Main file path: app.py
```

**App URL (optional):**
- **Custom subdomain:** `hai-facilities-dashboard` (or your choice)
- **Full URL will be:** `https://hai-facilities-dashboard.streamlit.app`

**Advanced settings (click "Advanced settings"):**
- **Python version:** 3.11 (recommended) or 3.10
- **Secrets:** (We'll configure this in the next step)

### 4.3 Initial Deployment

**Do NOT click "Deploy!" yet** - we need to configure secrets first!

Instead:
1. **Click:** "Advanced settings"
2. **Proceed to Step 5** to configure secrets

---

## Step 5: Configure Secrets (Critical)

This is the **most important step**. Without proper secrets configuration, your app will fail to connect to BigQuery.

### 5.1 Understanding Streamlit Secrets

Streamlit Community Cloud uses TOML format for secrets. The secrets are injected as environment variables and can be accessed via `st.secrets` in your app.

### 5.2 Create Secrets Configuration

In the **"Secrets"** section of Advanced settings, paste the following TOML configuration:

```toml
# Environment Variables
GCP_PROJECT_ID = "hai-dev"
BQ_DATASET = "facilities"

# BigQuery Service Account Credentials
[gcp_service_account]
type = "service_account"
project_id = "hai-dev"
private_key_id = "YOUR_PRIVATE_KEY_ID"
private_key = "-----BEGIN PRIVATE KEY-----\nYOUR_PRIVATE_KEY_CONTENT\n-----END PRIVATE KEY-----\n"
client_email = "streamlit-bigquery-reader@hai-dev.iam.gserviceaccount.com"
client_id = "YOUR_CLIENT_ID"
auth_uri = "https://accounts.google.com/o/oauth2/auth"
token_uri = "https://oauth2.googleapis.com/token"
auth_provider_x509_cert_url = "https://www.googleapis.com/oauth2/v1/certs"
client_x509_cert_url = "YOUR_CLIENT_CERT_URL"
universe_domain = "googleapis.com"
```

### 5.3 Fill in Service Account Details

**Important:** Replace the placeholder values with actual values from your downloaded JSON key:

1. Open your service account JSON file (from Step 2.4)
2. Copy each field **exactly** from the JSON to the TOML:
   - `private_key_id` → Copy the value
   - `private_key` → Copy the **entire** private key including `-----BEGIN PRIVATE KEY-----` and `-----END PRIVATE KEY-----`
   - `client_email` → Copy the value
   - `client_id` → Copy the value
   - `client_x509_cert_url` → Copy the value

**⚠️ Important Notes:**
- Keep all newline characters (`\n`) in the private_key
- Keep quotes around all string values
- Don't add extra spaces or line breaks
- The TOML format is sensitive to formatting

### 5.4 Verify Secrets Format

Your final secrets should look like this (with real values):

```toml
GCP_PROJECT_ID = "hai-dev"
BQ_DATASET = "facilities"

[gcp_service_account]
type = "service_account"
project_id = "hai-dev"
private_key_id = "1a2b3c4d5e6f7g8h9i0j"
private_key = "-----BEGIN PRIVATE KEY-----\nMIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQC...\n-----END PRIVATE KEY-----\n"
client_email = "streamlit-bigquery-reader@hai-dev.iam.gserviceaccount.com"
client_id = "123456789012345678901"
auth_uri = "https://accounts.google.com/o/oauth2/auth"
token_uri = "https://oauth2.googleapis.com/token"
auth_provider_x509_cert_url = "https://www.googleapis.com/oauth2/v1/certs"
client_x509_cert_url = "https://www.googleapis.com/robot/v1/metadata/x509/streamlit-bigquery-reader%40hai-dev.iam.gserviceaccount.com"
universe_domain = "googleapis.com"
```

### 5.5 Update BigQuery Client Code (if needed)

Your `database/bigquery_client.py` should access secrets like this:

```python
import streamlit as st
from google.cloud import bigquery
from google.oauth2 import service_account

@st.cache_resource
def get_bigquery_client():
    """Create and cache BigQuery client with service account credentials."""
    try:
        # Try to get credentials from Streamlit secrets (for cloud deployment)
        if hasattr(st, 'secrets') and 'gcp_service_account' in st.secrets:
            credentials = service_account.Credentials.from_service_account_info(
                st.secrets["gcp_service_account"]
            )
            project_id = st.secrets.get("GCP_PROJECT_ID", "hai-dev")
            client = bigquery.Client(credentials=credentials, project=project_id)
            return client
    except Exception as e:
        st.warning(f"Could not use Streamlit secrets: {e}")

    # Fallback to local authentication (for local development)
    try:
        from google.auth import default
        credentials, project = default()
        client = bigquery.Client(credentials=credentials, project=project)
        return client
    except Exception as e:
        st.error(f"Failed to initialize BigQuery client: {str(e)}")
        return None
```

**Check if this code exists** in your `bigquery_client.py`. If not, you'll need to update it.

### 5.6 Deploy the App

Now you're ready!

1. **Review all settings** one more time
2. **Click:** "Deploy!" button
3. **Wait for deployment** (usually 2-5 minutes)

You'll see:
- ✅ Building app...
- ✅ Installing dependencies...
- ✅ Starting app...
- ✅ App is live!

---

## Step 6: Advanced Configuration

### 6.1 Custom Domain (Optional)

If you want a custom subdomain:

1. Go to app settings (three dots ⋮ menu)
2. Click "Settings"
3. Update "App URL"
4. Save changes

### 6.2 Python Version

Recommended Python version: **3.11**

To specify explicitly, create `.streamlit/config.toml` in your repo:

```toml
[server]
enableCORS = false
enableXsrfProtection = false

[runner]
magicEnabled = true

[python]
version = "3.11"
```

### 6.3 Resource Management

Streamlit Community Cloud limits (free tier):
- **CPU:** 1 vCPU
- **Memory:** 1 GB RAM
- **Storage:** Limited
- **Inactive app shutdown:** After 7 days of inactivity

**Optimization Tips:**
- Use `@st.cache_data` and `@st.cache_resource` (already implemented)
- Limit default query results (use LIMIT clauses)
- Avoid loading entire tables into memory

### 6.4 App Sleep Settings

Apps sleep after inactivity to save resources. Users will see a "Wake up" button.

To keep your app active:
- Visit it regularly
- Consider upgrading to Streamlit for Teams (paid)

---

## Step 7: Testing & Verification

### 7.1 Access Your Live App

1. **URL:** `https://YOUR-APP-NAME.streamlit.app`
2. **Wait for app to load** (first load may take 30-60 seconds)

### 7.2 Test BigQuery Connection

1. **Navigate to Price Analysis tab**
2. **Select a Data Collection Period** from the sidebar
3. **Verify data loads** without errors
4. **Check all visualizations** render correctly

### 7.3 Test All Features

**Checklist:**
- [ ] Price Analysis tab loads data
- [ ] All filters work (Country, Period, Region, Sector)
- [ ] Phase 1-6 visualizations render
- [ ] Charts are interactive (hover, zoom)
- [ ] No authentication errors in console
- [ ] Page loads in under 10 seconds

### 7.4 Check Logs

If you encounter errors:

1. **Go to:** App settings (three dots ⋮)
2. **Click:** "Logs"
3. **Review:** Error messages and stack traces
4. **Look for:** Authentication errors, import errors, or BigQuery errors

### 7.5 Monitor Performance

- **Initial load time:** Should be < 30 seconds
- **Query execution:** First query may be slow, subsequent queries cached
- **Memory usage:** Monitor in logs for memory warnings

---

## Step 8: Troubleshooting

### Issue 1: Authentication Errors

**Symptoms:**
```
Error: Could not authenticate with BigQuery
DefaultCredentialsError: Could not automatically determine credentials
```

**Solutions:**
1. **Verify secrets are configured** (Step 5)
2. **Check TOML format** - no syntax errors
3. **Verify service account email** matches JSON key
4. **Check private_key format** - must include `\n` characters
5. **Restart app** - Settings → Reboot app

### Issue 2: Module Import Errors

**Symptoms:**
```
ModuleNotFoundError: No module named 'google'
ImportError: cannot import name 'bigquery'
```

**Solutions:**
1. **Check requirements.txt** exists and includes all dependencies
2. **Verify requirements.txt content:**
   ```
   streamlit>=1.28.0
   google-cloud-bigquery>=3.11.0
   pandas>=2.0.0
   python-dotenv>=1.0.0
   plotly>=5.17.0
   db-dtypes>=1.1.1
   ```
3. **Trigger redeploy** - Make a small change and push to GitHub

### Issue 3: BigQuery Permission Errors

**Symptoms:**
```
403 Forbidden: Access Denied
Permission denied on dataset facilities
```

**Solutions:**
1. **Verify service account has BigQuery Data Viewer role**
2. **Check project ID** matches in secrets
3. **Verify dataset name** is correct (`facilities`)
4. **Grant additional permissions** in GCP Console

### Issue 4: App Crashes or Hangs

**Symptoms:**
- App shows "Oh no!" error
- Infinite loading spinner
- Out of memory errors

**Solutions:**
1. **Check memory usage** in logs
2. **Reduce query LIMIT** values
3. **Optimize caching** - use `@st.cache_data` more aggressively
4. **Avoid loading large DataFrames** all at once

### Issue 5: Secrets Not Loading

**Symptoms:**
```
KeyError: 'gcp_service_account'
AttributeError: 'Secrets' object has no attribute 'gcp_service_account'
```

**Solutions:**
1. **Go to app settings** → Secrets
2. **Verify secrets exist** and are properly formatted
3. **Check for typos** in secret names
4. **Restart app** after updating secrets
5. **Verify TOML syntax** - use TOML validator online

### Issue 6: "Too Many Requests" Errors

**Symptoms:**
```
429 Too Many Requests
BigQuery quota exceeded
```

**Solutions:**
1. **Reduce query frequency** - increase cache TTL
2. **Optimize queries** - use more WHERE clauses
3. **Check BigQuery quotas** in GCP Console
4. **Wait and retry** - quotas reset over time

### How to Access Logs

1. Go to your app URL
2. Click three dots (⋮) in bottom right
3. Click "Manage app"
4. Click "Logs" tab
5. Look for red error messages

---

## Maintenance & Updates

### 9.1 Deploying Updates

**Automatic Deployment:**
Streamlit Community Cloud automatically deploys when you push to GitHub.

```bash
# Make changes to your code
git add .
git commit -m "Update: Added new feature"
git push origin main
```

The app will automatically rebuild and redeploy (2-3 minutes).

### 9.2 Manual Reboot

To manually restart your app:

1. Go to app settings (three dots ⋮)
2. Click "Reboot app"
3. Wait for restart (30-60 seconds)

### 9.3 Updating Secrets

To update service account credentials or environment variables:

1. Go to app settings → "Secrets"
2. Edit the TOML configuration
3. Click "Save"
4. App will automatically restart

### 9.4 Rotating Service Account Keys

**Recommended:** Rotate keys every 90 days

1. **Create new key** in GCP Console
2. **Update secrets** in Streamlit Cloud
3. **Test app** to verify new key works
4. **Delete old key** in GCP Console

### 9.5 Monitoring App Health

**Check regularly:**
- [ ] App is accessible (not sleeping)
- [ ] Data is loading correctly
- [ ] No errors in logs
- [ ] Performance is acceptable

**Set up monitoring:**
- Use GCP BigQuery monitoring for query patterns
- Check Streamlit analytics (if available)
- Set up external uptime monitoring (UptimeRobot, etc.)

### 9.6 Handling App Sleep

Free tier apps sleep after 7 days of inactivity.

**To wake up:**
- Visit the app URL
- Click "Wake up" button
- Wait 30-60 seconds for startup

**To prevent sleep:**
- Upgrade to Streamlit for Teams
- Or visit app regularly

---

## Appendices

### Appendix A: Complete Secrets Template

Save this as reference: `secrets.toml.template`

```toml
# HAI Facilities Dashboard - Streamlit Cloud Secrets Configuration
# Copy this template and fill in your actual values

# Environment Variables
GCP_PROJECT_ID = "hai-dev"
BQ_DATASET = "facilities"

# BigQuery Service Account Credentials
# Replace ALL values below with your actual service account JSON key values
[gcp_service_account]
type = "service_account"
project_id = "hai-dev"
private_key_id = "REPLACE_WITH_YOUR_PRIVATE_KEY_ID"
private_key = "-----BEGIN PRIVATE KEY-----\nREPLACE_WITH_YOUR_PRIVATE_KEY\n-----END PRIVATE KEY-----\n"
client_email = "REPLACE_WITH_YOUR_SERVICE_ACCOUNT_EMAIL"
client_id = "REPLACE_WITH_YOUR_CLIENT_ID"
auth_uri = "https://accounts.google.com/o/oauth2/auth"
token_uri = "https://oauth2.googleapis.com/token"
auth_provider_x509_cert_url = "https://www.googleapis.com/oauth2/v1/certs"
client_x509_cert_url = "REPLACE_WITH_YOUR_CLIENT_CERT_URL"
universe_domain = "googleapis.com"
```

### Appendix B: Pre-Deployment Checklist

Before deploying, verify:

**Repository:**
- [ ] Code pushed to GitHub
- [ ] `.gitignore` excludes `.env` and `credentials/`
- [ ] `requirements.txt` is complete
- [ ] `app.py` is in root directory
- [ ] All imports work locally

**BigQuery:**
- [ ] Service account created
- [ ] JSON key downloaded
- [ ] Permissions granted (BigQuery Data Viewer)
- [ ] Project ID correct (`hai-dev`)
- [ ] Dataset exists (`facilities`)

**Streamlit Cloud:**
- [ ] Account created
- [ ] GitHub connected
- [ ] Secrets configured in TOML format
- [ ] All secret values copied from JSON key

**Testing:**
- [ ] App runs locally with `streamlit run app.py`
- [ ] BigQuery connection works locally
- [ ] No hardcoded credentials in code

### Appendix C: Post-Deployment Checklist

After deployment:

- [ ] App URL is accessible
- [ ] Price Analysis tab loads data
- [ ] All 6 phases display correctly
- [ ] Filters work (Country, Period, Region, Sector)
- [ ] Charts render and are interactive
- [ ] No errors in logs
- [ ] Performance is acceptable (< 30s load time)
- [ ] Share URL with stakeholders

### Appendix D: Useful Links

**Streamlit Documentation:**
- Streamlit Cloud: https://docs.streamlit.io/streamlit-community-cloud
- Secrets Management: https://docs.streamlit.io/streamlit-community-cloud/deploy-your-app/secrets-management
- Troubleshooting: https://docs.streamlit.io/knowledge-base/deploy

**Google Cloud Documentation:**
- Service Accounts: https://cloud.google.com/iam/docs/service-accounts
- BigQuery Authentication: https://cloud.google.com/bigquery/docs/authentication
- IAM Roles: https://cloud.google.com/bigquery/docs/access-control

**GitHub:**
- GitHub Docs: https://docs.github.com
- Git Basics: https://git-scm.com/book/en/v2

**Support:**
- Streamlit Forum: https://discuss.streamlit.io
- Streamlit GitHub: https://github.com/streamlit/streamlit

### Appendix E: Security Best Practices

**DO:**
- ✅ Use service accounts with minimal permissions
- ✅ Keep JSON keys secure and never commit to GitHub
- ✅ Rotate service account keys regularly (every 90 days)
- ✅ Use `.gitignore` to exclude credentials
- ✅ Make repository private if handling sensitive data
- ✅ Review Streamlit Cloud access logs regularly

**DON'T:**
- ❌ Commit `.env` files to GitHub
- ❌ Hardcode credentials in source code
- ❌ Share service account JSON keys via email/Slack
- ❌ Use personal Google account credentials
- ❌ Grant more permissions than necessary
- ❌ Leave old service account keys active

### Appendix F: Cost Considerations

**Streamlit Community Cloud (Free Tier):**
- **Cost:** $0/month
- **Apps:** 1 public app or 1 private app
- **Resources:** 1 GB RAM, 1 vCPU per app
- **Limitations:** App sleeps after 7 days inactivity

**Google Cloud BigQuery:**
- **Storage:** $0.02 per GB per month (first 10 GB free)
- **Queries:** $5 per TB scanned (first 1 TB per month free)
- **Expected cost for this app:** $0-5/month (typical usage)

**Upgrades Available:**
- Streamlit for Teams: $250/month (unlimited apps, no sleep)
- Streamlit Enterprise: Custom pricing

---

## Summary

You've successfully deployed your HAI Facilities Dashboard to Streamlit Community Cloud! 🎉

**Key takeaways:**
1. GitHub integration enables automatic deployments
2. Service account credentials must be properly configured in secrets
3. TOML format is used for all secrets in Streamlit Cloud
4. Monitor logs regularly for errors
5. Rotate service account keys every 90 days

**Next steps:**
- Share your app URL with stakeholders
- Set up monitoring for uptime and performance
- Plan regular maintenance and updates
- Consider upgrading if you need more resources

**Need help?**
- Check Streamlit Community Forum: https://discuss.streamlit.io
- Review BigQuery docs: https://cloud.google.com/bigquery/docs
- Open GitHub issues for bugs in your repository

---

**Document Version:** 1.0
**Last Updated:** December 9, 2025
**Author:** HAI Development Team
**Application:** HAI Facilities Data Dashboard
