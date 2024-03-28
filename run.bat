@echo off 

IF NOT EXIST setup.txt (
	echo --- Initialing environment... 
	call .\setup.bat 
) 

echo --- Activating venv... 
call .\venv\Scripts\activate 

echo --- Starting game... 
python main.py 
