@echo off
call .\env\Scripts\activate
python -m uvicorn transcriber_api:app --reload
pause
