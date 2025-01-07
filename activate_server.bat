@echo off

REM Activate the virtual environment
call env\Scripts\activate

REM Start the Uvicorn server
uvicorn main:app --reload

REM Pause to keep the window open after execution
pause
