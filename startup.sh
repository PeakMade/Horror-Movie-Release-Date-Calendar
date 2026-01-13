# Startup script for Azure App Service
echo "Starting Horror Movie Calendar App..."
echo "Python version:"
python --version
echo "Installing dependencies..."
python -m pip install --upgrade pip
pip install -r requirements.txt
echo "Starting Flask application..."
python main.py