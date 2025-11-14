# CI/CD Setup for PythonAnywhere

## Problem Fixed

Your GitHub CI was failing with 404 errors due to:
1. Empty environment variables (GitHub Secrets not configured)
2. Wrong API endpoint (`/consoles/bash/send_input` doesn't exist)
3. No error handling or testing pipeline

## Solution

Created proper CI/CD pipeline with:
- Correct PythonAnywhere API endpoints
- GitHub Actions workflows for testing and deployment
- Automated deployment scripts

## Setup Instructions

### 1. Configure GitHub Secrets

Go to: GitHub repo > Settings > Secrets and variables > Actions

Add 3 secrets:
- `PYTHONANYWHERE_USERNAME` - Your PythonAnywhere username
- `PYTHONANYWHERE_API_TOKEN` - Get from https://www.pythonanywhere.com/account/
- `PYTHONANYWHERE_DOMAIN` - Format: username.pythonanywhere.com

### 2. Set Up PythonAnywhere

On PythonAnywhere bash console:

```bash
cd ~
git clone https://github.com/YOUR_USERNAME/comp5313_gr3_projects.git
cd comp5313_gr3_projects
python3.10 -m venv venv
source venv/bin/activate
pip install -r backend/requirements.txt
```

Upload `dialogflow_key.json` to `~/comp5313_gr3_projects/backend/`

### 3. Configure Web App

In PythonAnywhere Web tab, set:
- Source code: `/home/YOUR_USERNAME/comp5313_gr3_projects/backend`
- Working directory: `/home/YOUR_USERNAME/comp5313_gr3_projects/backend`
- WSGI file: `/home/YOUR_USERNAME/comp5313_gr3_projects/backend/wsgi.py`
- Virtualenv: `/home/YOUR_USERNAME/comp5313_gr3_projects/venv`

### 4. Set Up Scheduled Task

In PythonAnywhere Tasks tab:
```bash
cd ~/comp5313_gr3_projects && git pull origin main
```
Schedule: Daily at 00:00 UTC

### 5. Test Deployment

```bash
curl https://YOUR_DOMAIN.pythonanywhere.com/health
```

## How It Works

1. Push code to main branch
2. GitHub Actions runs tests (`.github/workflows/test.yml`)
3. If tests pass, deployment workflow runs (`.github/workflows/deploy.yml`)
4. Deployment script calls PythonAnywhere API to reload web app
5. Scheduled task keeps code in sync with GitHub

## Files

- `workflows/deploy.yml` - Production deployment workflow
- `workflows/test.yml` - Testing and linting workflow
- `scripts/deploy_pythonanywhere.py` - Main deployment script
- `scripts/setup_pythonanywhere.sh` - Initial PythonAnywhere setup helper
- `scripts/auto_pull.sh` - Auto git pull script for scheduled tasks

## Troubleshooting

**404 Error**
- Verify all 3 GitHub Secrets are set correctly
- Check domain format: username.pythonanywhere.com
- Ensure web app exists on PythonAnywhere

**Code Not Updating**
- Check scheduled task is running
- Manually run: `cd ~/comp5313_gr3_projects && git pull origin main`

**Import Errors**
- Activate venv: `source ~/comp5313_gr3_projects/venv/bin/activate`
- Reinstall: `pip install -r backend/requirements.txt`

**Dialogflow Errors**
- Verify `dialogflow_key.json` exists at `~/comp5313_gr3_projects/backend/`
- Check file permissions
