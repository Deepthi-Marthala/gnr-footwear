@echo off
echo.
echo  ================================
echo    GNR Footwear Store - Starting
echo  ================================
echo.
cd backend
pip install flask flask-cors -q
echo  Starting server...
echo.
echo  Open browser: http://127.0.0.1:5000
echo  Admin panel:  http://127.0.0.1:5000  click Admin tab
echo.
python app.py
pause
