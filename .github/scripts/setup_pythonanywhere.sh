#!/bin/bash
# Setup script to run on PythonAnywhere for initial configuration
# Run this script once on PythonAnywhere bash console

set -e

echo "=========================================="
echo "PythonAnywhere Initial Setup Script"
echo "=========================================="
echo ""

# Configuration
REPO_URL="https://github.com/YOUR_USERNAME/comp5313_gr3_projects.git"
PROJECT_DIR="$HOME/comp5313_gr3_projects"
PYTHON_VERSION="3.10"

# Step 1: Clone repository (if not exists)
if [ -d "$PROJECT_DIR" ]; then
    echo "[1/5] Repository already exists, pulling latest changes..."
    cd "$PROJECT_DIR"
    git checkout main
    git pull origin main
else
    echo "[1/5] Cloning repository..."
    git clone "$REPO_URL" "$PROJECT_DIR"
    cd "$PROJECT_DIR"
fi

# Step 2: Create virtual environment
echo ""
echo "[2/5] Setting up virtual environment..."
if [ ! -d "venv" ]; then
    python${PYTHON_VERSION} -m venv venv
    echo "Virtual environment created"
else
    echo "Virtual environment already exists"
fi

# Step 3: Activate and install dependencies
echo ""
echo "[3/5] Installing dependencies..."
source venv/bin/activate
pip install --upgrade pip
pip install -r backend/requirements.txt

# Step 4: Check for Dialogflow credentials
echo ""
echo "[4/5] Checking Dialogflow credentials..."
if [ ! -f "$PROJECT_DIR/backend/dialogflow_key.json" ]; then
    echo "WARNING: dialogflow_key.json not found!"
    echo "Please upload this file to: $PROJECT_DIR/backend/dialogflow_key.json"
    echo ""
else
    echo "Dialogflow credentials found"
fi

# Step 5: Display next steps
echo ""
echo "[5/5] Setup complete!"
echo ""
echo "=========================================="
echo "Next Steps:"
echo "=========================================="
echo "1. Configure Web App in PythonAnywhere dashboard:"
echo "   - Source code: $PROJECT_DIR/backend"
echo "   - Working directory: $PROJECT_DIR/backend"
echo "   - WSGI file: $PROJECT_DIR/backend/wsgi.py"
echo "   - Virtualenv: $PROJECT_DIR/venv"
echo ""
echo "2. Upload dialogflow_key.json to: $PROJECT_DIR/backend/"
echo ""
echo "3. Set up scheduled task (optional) for auto git pull:"
echo "   Command: cd $PROJECT_DIR && git pull origin main"
echo "   Frequency: Daily at 00:00"
echo ""
echo "4. Test your deployment:"
echo "   curl https://YOUR_DOMAIN.pythonanywhere.com/health"
echo ""
echo "=========================================="

