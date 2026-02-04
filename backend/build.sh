#!/usr/bin/env bash
# Render build script

set -o errexit

pip install --upgrade pip
pip install -r requirements.txt

# Initialize database tables
python -c "from app import create_app; app = create_app(); print('Database tables created successfully!')"
