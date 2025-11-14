#!/bin/bash
# Auto-pull script for PythonAnywhere scheduled tasks
# This script should be set up as a scheduled task to run periodically

set -e

PROJECT_DIR="$HOME/comp5313_gr3_projects"

echo "$(date): Starting auto-pull..."

cd "$PROJECT_DIR"

# Fetch latest changes
git fetch origin main

# Check if there are updates
LOCAL=$(git rev-parse @)
REMOTE=$(git rev-parse @{u})

if [ "$LOCAL" != "$REMOTE" ]; then
    echo "$(date): Updates found, pulling changes..."
    git pull origin main
    echo "$(date): Pull complete"
    
    # Optional: Automatically reload web app via API
    # Requires API token set as environment variable
    if [ -n "$PYTHONANYWHERE_API_TOKEN" ] && [ -n "$PYTHONANYWHERE_DOMAIN" ]; then
        curl -X POST \
            "https://www.pythonanywhere.com/api/v0/user/$(whoami)/webapps/${PYTHONANYWHERE_DOMAIN}/reload/" \
            -H "Authorization: Token ${PYTHONANYWHERE_API_TOKEN}"
        echo "$(date): Web app reloaded"
    fi
else
    echo "$(date): Already up to date"
fi

