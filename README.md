# 🛍️ GNR Footwear — Full Stack Store
### React + Flask + SQLite

---

## 📁 Project Structure
```
gnr-fullstack/
├── backend/
│   ├── app.py           ← Flask API server
│   ├── requirements.txt ← Python packages
│   └── gnr.db           ← SQLite database (auto-created)
├── frontend/
│   ├── src/App.js       ← Full React app
│   ├── public/index.html
│   └── package.json
├── start-windows.bat    ← Double-click to start on Windows
└── start-mac-linux.sh  ← Run on Mac/Linux
```

---

## 🚀 How to Run Locally

### Requirements
- Python 3.8+ installed
- Node.js 16+ installed
- pip (comes with Python)
- npm (comes with Node.js)

### Windows
```
Double-click: start-windows.bat
```

### Mac / Linux
```bash
chmod +x start-mac-linux.sh
./start-mac-linux.sh
```

### Manual (step by step)
```bash
# Terminal 1 — Backend
cd backend
pip install -r requirements.txt
python app.py

# Terminal 2 — Frontend
cd frontend
npm install
npm start
```

---

## 🌐 URLs
| Page | URL |
|------|-----|
| Store (Home) | http://localhost:3000 |
| Products | http://localhost:3000 (click Products) |
| Admin Panel | http://localhost:3000 (click Admin) |
| API | http://localhost:5000/api/products |

---

## 📦 API Endpoints (Flask)
| Method | URL | Action |
|--------|-----|--------|
| GET | /api/products | Get all products |
| GET | /api/products?category=crocs | Filter by category |
| POST | /api/products | Add new product |
| PUT | /api/products/:id | Update product |
| DELETE | /api/products/:id | Delete product |
| GET | /api/stats | Get store stats |

---

## ☁️ Free Cloud Deployment

### Backend (Render.com — Free)
1. Go to render.com → New → Web Service
2. Upload backend folder
3. Build Command: `pip install -r requirements.txt`
4. Start Command: `python app.py`
5. Copy your backend URL

### Frontend (Netlify — Free)
1. In frontend/package.json, change `"proxy"` to your Render backend URL
2. Run: `npm run build`
3. Drag `build/` folder to netlify.com
4. Done! Free URL

---

## 📲 WhatsApp Orders
In `frontend/src/App.js`, search for `91XXXXXXXXXX` and replace with your WhatsApp number.

---

## 🏪 Stores
- **GNR Footwear 1** — Beside Kasam Shopping Mall, Bhadrachalam
- **GNR Footwear 2** — Beside Apollo Pharmacy, UB Road, Bhadrachalam
