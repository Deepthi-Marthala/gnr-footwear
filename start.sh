#!/bin/bash
echo ""
echo "================================"
echo "  GNR Footwear Store - Starting"
echo "================================"
cd backend
pip3 install flask flask-cors -q
echo ""
echo "  Open browser: http://127.0.0.1:5000"
echo "  Admin panel:  http://127.0.0.1:5000 → click Admin"
echo ""
python3 app.py
