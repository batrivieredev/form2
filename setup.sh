#!/bin/bash

echo "Creating virtual environment..."
python3 -m venv venv

echo "Activating virtual environment..."
source venv/bin/activate

echo "Installing Python dependencies..."
pip install -r backend/requirements.txt

echo "Creating uploads directory..."
mkdir -p uploads

echo "Creating MySQL database..."
mysql -u root -e "CREATE DATABASE IF NOT EXISTS form_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"

echo "Initializing database..."
flask db init
flask db migrate -m "Initial migration"
flask db upgrade

echo "Setup completed successfully!"
echo "To start the application, run: python run.py"
