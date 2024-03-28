@echo off 

echo - Updating pip... 
python -m ensurepip 

echo - Installing virtualenv...
python -m pip install virtualenv

echo - Setting up venv... 
python -m virtualenv venv 

echo - Activating venv...
call .\venv\Scripts\activate 

echo - Installing requirements... 
python -m ensurepip 
python -m pip install -r requirements.txt 

echo 'Successful setup' > setup.logs 