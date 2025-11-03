@echo off
echo Starting deployment process...
echo Installing dependencies...
python -m pip install --upgrade pip
pip install -r requirements.txt
echo Dependencies installed successfully.
echo Deployment completed successfully.