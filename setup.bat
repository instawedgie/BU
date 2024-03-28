@echo off 

echo "--- Start Setup ---" > setup.logs

echo - Updating pip... 
python -m ensurepip >> setup.logs 2>&1

echo - Installing virtualenv...
python -m pip install virtualenv >> setup.logs 2>&1

echo - Setting up venv... 
python -m virtualenv venv >> setup.logs 2>&1

echo - Activating venv...
call .\venv\Scripts\activate >> setup.logs 2>&1

echo - Installing requirements... 
python -m ensurepip >> setup.logs 2>&1
python -m pip install -r requirements.txt >> setup.logs 2>&1

echo 'Game Fully Setup' > setup.txt
