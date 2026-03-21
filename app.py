from flask import Flask, request, jsonify, Response
from flask_cors import CORS
import sqlite3, os

app = Flask(__name__)
CORS(app)
DB_PATH = os.path.join(os.path.dirname(__file__), 'gnr.db')

# ── DATABASE ──────────────────────────────────────────

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    conn.execute('''CREATE TABLE IF NOT EXISTS products (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL, category TEXT NOT NULL,
        price REAL NOT NULL, original_price REAL DEFAULT 0,
        discount INTEGER DEFAULT 0, image TEXT DEFAULT '',
        description TEXT DEFAULT '', extra TEXT DEFAULT '',
        is_new INTEGER DEFAULT 1, in_stock INTEGER DEFAULT 1,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
    if conn.execute('SELECT COUNT(*) FROM products').fetchone()[0] == 0:
        conn.executemany('''INSERT INTO products
            (name,category,price,original_price,discount,image,description,extra,is_new,in_stock)
            VALUES (?,?,?,?,?,?,?,?,?,?)''', [
            ('Classic Crocs Clog','crocs',799,1299,38,'https://images.unsplash.com/photo-1606107557195-0e29a4b5b4aa?w=400&q=80','Comfortable everyday crocs. Lightweight and water-resistant.','',1,1),
            ('Chunky Sports Shoes','shoes',1299,2199,41,'https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=400&q=80','Trendy chunky sneakers. Available in multiple colours.','',0,1),
            ('Gold Chain Necklace','jewellery',649,999,35,'https://images.unsplash.com/photo-1515562141207-7a88fb7ce338?w=400&q=80','Premium gold-plated chain necklace. Perfect for all occasions.','',1,1),
            ('Flip Flop Slides','crocs',499,799,37,'https://images.unsplash.com/photo-1562183241-b937e95585b6?w=400&q=80','Soft padded flip flop slides. Ultra comfortable.','',0,1),
            ("Women's Heels",'shoes',1099,1799,38,'https://images.unsplash.com/photo-1543163521-1bf539c55dd2?w=400&q=80','Elegant block heels for parties and everyday wear.','',1,1),
            ('Silver Earrings Set','jewellery',349,599,41,'https://images.unsplash.com/photo-1535632066927-ab7c9ab60908?w=400&q=80','Trendy silver earring set — 3 pairs. Light and stylish.','',0,1),
        ])
    conn.commit(); conn.close()

# ── API ───────────────────────────────────────────────

@app.route('/api/products', methods=['GET'])
def get_products():
    cat = request.args.get('category')
    conn = get_db()
    if cat and cat != 'all':
        rows = conn.execute('SELECT * FROM products WHERE category=? ORDER BY id DESC',(cat,)).fetchall()
    else:
        rows = conn.execute('SELECT * FROM products ORDER BY id DESC').fetchall()
    conn.close()
    return jsonify([dict(r) for r in rows])

@app.route('/api/products', methods=['POST'])
def add_product():
    d = request.json
    if not d.get('name') or not d.get('price'):
        return jsonify({'error':'name and price required'}), 400
    conn = get_db()
    cur = conn.execute('''INSERT INTO products
        (name,category,price,original_price,discount,image,description,extra,is_new,in_stock)
        VALUES (?,?,?,?,?,?,?,?,?,?)''', (
        d['name'], d.get('category','crocs'), float(d['price']),
        float(d.get('original_price',0)), int(d.get('discount',0)),
        d.get('image',''), d.get('description',''), d.get('extra',''),
        1 if d.get('is_new',True) else 0, 1 if d.get('in_stock',True) else 0))
    conn.commit()
    row = conn.execute('SELECT * FROM products WHERE id=?',(cur.lastrowid,)).fetchone()
    conn.close()
    return jsonify(dict(row)), 201

@app.route('/api/products/<int:pid>', methods=['PUT'])
def update_product(pid):
    d = request.json
    conn = get_db()
    conn.execute('''UPDATE products SET name=?,category=?,price=?,original_price=?,
        discount=?,image=?,description=?,extra=?,is_new=?,in_stock=? WHERE id=?''', (
        d['name'], d.get('category','crocs'), float(d['price']),
        float(d.get('original_price',0)), int(d.get('discount',0)),
        d.get('image',''), d.get('description',''), d.get('extra',''),
        1 if d.get('is_new',True) else 0, 1 if d.get('in_stock',True) else 0, pid))
    conn.commit()
    row = conn.execute('SELECT * FROM products WHERE id=?',(pid,)).fetchone()
    conn.close()
    return jsonify(dict(row) if row else {'error':'not found'})

@app.route('/api/products/<int:pid>', methods=['DELETE'])
def delete_product(pid):
    conn = get_db()
    conn.execute('DELETE FROM products WHERE id=?',(pid,))
    conn.commit(); conn.close()
    return jsonify({'deleted':pid})

@app.route('/api/stats')
def stats():
    conn = get_db()
    total = conn.execute('SELECT COUNT(*) FROM products').fetchone()[0]
    instock = conn.execute('SELECT COUNT(*) FROM products WHERE in_stock=1').fetchone()[0]
    conn.close()
    return jsonify({'total':total,'in_stock':instock,'categories':3})

# ── SERVE STORE ───────────────────────────────────────

@app.route('/')
@app.route('/admin')
def index():
    return Response(HTML, mimetype='text/html')

# ── HTML STORE (full page embedded) ──────────────────

HTML = r"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8"/>
  <meta name="viewport" content="width=device-width,initial-scale=1"/>
  <title>GNR Footwear – Crocs, Shoes & Jewellery | Bhadrachalam</title>
  <link href="https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700;900&family=DM+Sans:wght@300;400;500;600&display=swap" rel="stylesheet"/>
  <style>
    :root{--gold:#C9A84C;--goldL:#E8CC7E;--dark:#0D0D0D;--dark2:#181818;--dark3:#242424;--text:#F0EDE8;--muted:#888;--accent:#E63946;--green:#2d9e5f;}
    *{margin:0;padding:0;box-sizing:border-box;}html{scroll-behavior:smooth;}
    body{background:var(--dark);color:var(--text);font-family:'DM Sans',sans-serif;overflow-x:hidden;}
    ::-webkit-scrollbar{width:5px;}::-webkit-scrollbar-thumb{background:var(--gold);border-radius:3px;}
    @keyframes fadeUp{from{opacity:0;transform:translateY(20px);}to{opacity:1;transform:translateY(0);}}
    @keyframes marquee{0%{transform:translateX(0);}100%{transform:translateX(-50%);}}
    @keyframes spin{to{transform:rotate(360deg);}}
    /* NAV */
    nav{position:fixed;top:0;width:100%;z-index:200;background:rgba(13,13,13,.96);backdrop-filter:blur(12px);border-bottom:1px solid rgba(201,168,76,.15);padding:0 5%;}
    .nav-inner{display:flex;align-items:center;justify-content:space-between;height:64px;}
    .logo{display:flex;align-items:center;gap:10px;cursor:pointer;}
    .logo-box{width:42px;height:42px;background:linear-gradient(135deg,var(--gold),#8B6914);border-radius:10px;display:flex;align-items:center;justify-content:center;font-family:'Playfair Display',serif;font-weight:900;font-size:16px;color:#000;}
    .logo-name{font-family:'Playfair Display',serif;font-size:20px;font-weight:700;color:var(--gold);letter-spacing:2px;}
    .nav-links{display:flex;gap:24px;align-items:center;}
    .nav-btn{cursor:pointer;font-size:12px;letter-spacing:2px;text-transform:uppercase;color:var(--muted);transition:color .2s;background:none;border:none;font-family:'DM Sans',sans-serif;padding:4px 0;}
    .nav-btn:hover{color:var(--gold);}
    .nav-cart{position:relative;background:var(--gold);color:#000;border:none;padding:9px 22px;border-radius:8px;font-weight:700;font-size:13px;cursor:pointer;letter-spacing:1px;font-family:'DM Sans',sans-serif;transition:background .2s;}
    .nav-cart:hover{background:var(--goldL);}
    .cbadge{position:absolute;top:-7px;right:-7px;background:var(--accent);color:#fff;border-radius:50%;width:19px;height:19px;font-size:10px;display:none;align-items:center;justify-content:center;font-weight:700;}
    /* PAGES */
    .page{display:none;}.page.active{display:block;}
    /* HERO */
    .hero{height:100vh;background:linear-gradient(135deg,#0D0D0D,#1a1208,#0D0D0D);display:flex;align-items:center;justify-content:center;text-align:center;position:relative;overflow:hidden;padding-top:64px;}
    .hero::before{content:'';position:absolute;inset:0;background:radial-gradient(ellipse at 50% 40%,rgba(201,168,76,.13) 0%,transparent 70%);}
    .hero-c{position:relative;z-index:1;animation:fadeUp .8s ease;}
    .h-badge{background:rgba(201,168,76,.1);border:1px solid rgba(201,168,76,.3);color:var(--gold);padding:6px 20px;border-radius:50px;font-size:11px;letter-spacing:4px;text-transform:uppercase;display:inline-block;margin-bottom:24px;}
    .hero h1{font-family:'Playfair Display',serif;font-size:clamp(44px,8vw,88px);font-weight:900;line-height:1;margin-bottom:24px;}
    .hero h1 span{color:var(--gold);}
    .hero p{font-size:16px;color:var(--muted);max-width:460px;margin:0 auto 40px;line-height:1.8;}
    .hero-btns{display:flex;gap:16px;justify-content:center;flex-wrap:wrap;}
    .btn-p{background:var(--gold);color:#000;padding:14px 36px;border-radius:8px;font-weight:700;font-size:14px;border:none;cursor:pointer;letter-spacing:1px;font-family:'DM Sans',sans-serif;transition:all .2s;}
    .btn-p:hover{background:var(--goldL);transform:translateY(-2px);}
    .btn-o{background:transparent;color:var(--text);padding:14px 36px;border-radius:8px;font-weight:600;font-size:14px;border:1px solid rgba(255,255,255,.2);cursor:pointer;letter-spacing:1px;font-family:'DM Sans',sans-serif;transition:all .2s;}
    .btn-o:hover{border-color:var(--gold);color:var(--gold);}
    .hero-stats{position:absolute;bottom:40px;left:50%;transform:translateX(-50%);display:flex;gap:48px;}
    .snum{font-family:'Playfair Display',serif;font-size:28px;font-weight:700;color:var(--gold);}
    .slbl{font-size:11px;color:var(--muted);letter-spacing:2px;text-transform:uppercase;}
    /* STRIP */
    .strip{background:var(--gold);padding:10px 0;overflow:hidden;}
    .strip-i{display:flex;gap:48px;animation:marquee 20s linear infinite;white-space:nowrap;}
    .si{font-size:11px;font-weight:800;letter-spacing:3px;text-transform:uppercase;color:#000;}
    /* SECTIONS */
    .sec{padding:80px 5%;}
    .stag{font-size:11px;letter-spacing:4px;text-transform:uppercase;color:var(--gold);margin-bottom:12px;}
    .stitle{font-family:'Playfair Display',serif;font-size:clamp(26px,4vw,44px);font-weight:700;margin-bottom:40px;}
    .stitle span{color:var(--gold);}
    /* CATEGORIES */
    .cat-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:20px;}
    .cat-card{position:relative;border-radius:16px;overflow:hidden;cursor:pointer;aspect-ratio:3/4;background:var(--dark3);}
    .cat-card img{width:100%;height:100%;object-fit:cover;transition:transform .5s;}
    .cat-card:hover img{transform:scale(1.08);}
    .cat-ov{position:absolute;inset:0;background:linear-gradient(to top,rgba(0,0,0,.85) 0%,transparent 55%);}
    .cat-info{position:absolute;bottom:24px;left:24px;right:24px;}
    .cn{font-family:'Playfair Display',serif;font-size:22px;font-weight:700;margin-bottom:4px;}
    .cs{font-size:11px;color:var(--gold);letter-spacing:2px;margin-bottom:12px;}
    .cat-btn{background:var(--gold);color:#000;padding:8px 20px;border-radius:6px;font-size:12px;font-weight:700;border:none;cursor:pointer;letter-spacing:1px;font-family:'DM Sans',sans-serif;}
    /* PRODUCT GRID */
    .pgrid{display:grid;grid-template-columns:repeat(auto-fill,minmax(230px,1fr));gap:24px;}
    .pcard{background:var(--dark2);border-radius:16px;overflow:hidden;cursor:pointer;border:1px solid rgba(255,255,255,.04);transition:transform .3s,box-shadow .3s;}
    .pcard:hover{transform:translateY(-6px);box-shadow:0 20px 60px rgba(0,0,0,.5);}
    .pimgw{position:relative;aspect-ratio:1;background:var(--dark3);overflow:hidden;}
    .pimgw img{width:100%;height:100%;object-fit:cover;transition:transform .4s;}
    .pcard:hover .pimgw img{transform:scale(1.07);}
    .bdg{position:absolute;top:12px;font-size:10px;font-weight:700;padding:4px 10px;border-radius:4px;letter-spacing:1px;}
    .bdg-d{left:12px;background:var(--accent);color:#fff;}
    .bdg-n{right:12px;background:var(--gold);color:#000;}
    .bdg-oos{position:absolute;inset:0;background:rgba(0,0,0,.6);display:flex;align-items:center;justify-content:center;font-size:12px;font-weight:700;color:var(--accent);letter-spacing:2px;}
    .pbody{padding:16px;}
    .pclbl{font-size:11px;color:var(--muted);letter-spacing:2px;text-transform:uppercase;margin-bottom:4px;}
    .pname{font-weight:600;font-size:15px;margin-bottom:10px;}
    .pprices{display:flex;align-items:center;gap:8px;margin-bottom:12px;}
    .pprice{font-family:'Playfair Display',serif;font-size:20px;font-weight:700;color:var(--gold);}
    .porig{font-size:13px;color:var(--muted);text-decoration:line-through;}
    .psave{font-size:11px;color:var(--accent);font-weight:700;}
    .pactions{display:flex;gap:8px;}
    .bcart{flex:1;background:var(--gold);color:#000;border:none;padding:10px;border-radius:8px;font-weight:700;font-size:12px;cursor:pointer;transition:background .2s;font-family:'DM Sans',sans-serif;}
    .bcart:hover{background:var(--goldL);}
    .bcart.added{background:var(--green);}
    .bwish{background:rgba(255,255,255,.05);border:1px solid rgba(255,255,255,.1);color:var(--text);padding:10px 14px;border-radius:8px;cursor:pointer;}
    /* FILTERS */
    .fltrs{display:flex;gap:10px;margin-bottom:32px;flex-wrap:wrap;}
    .fbtn{background:transparent;border:1px solid rgba(255,255,255,.12);color:var(--muted);padding:8px 20px;border-radius:50px;font-size:13px;cursor:pointer;transition:all .2s;font-family:'DM Sans',sans-serif;}
    .fbtn.active,.fbtn:hover{background:var(--gold);color:#000;border-color:var(--gold);font-weight:700;}
    /* SALE */
    .sale-b{margin:0 5% 80px;background:linear-gradient(135deg,#1a1208,#2a1f08);border:1px solid rgba(201,168,76,.2);border-radius:24px;padding:60px 40px;text-align:center;}
    .sale-b h2{font-family:'Playfair Display',serif;font-size:clamp(26px,5vw,50px);font-weight:900;margin-bottom:16px;}
    .sale-b h2 span{color:var(--gold);}
    .cdwn{display:flex;gap:16px;justify-content:center;margin-bottom:28px;}
    .cdb{background:rgba(0,0,0,.4);border:1px solid rgba(201,168,76,.2);border-radius:12px;padding:16px 24px;text-align:center;min-width:80px;}
    .cdn{font-family:'Playfair Display',serif;font-size:30px;font-weight:700;color:var(--gold);}
    .cdl{font-size:10px;color:var(--muted);letter-spacing:2px;text-transform:uppercase;}
    /* STORES */
    .stores-g{display:grid;grid-template-columns:1fr 1fr;gap:20px;max-width:680px;}
    .store-c{background:var(--dark3);border-radius:16px;padding:24px;border:1px solid rgba(201,168,76,.15);}
    .store-t{font-family:'Playfair Display',serif;font-size:18px;font-weight:700;color:var(--gold);margin-bottom:8px;}
    /* MODAL */
    .mbg{display:none;position:fixed;inset:0;background:rgba(0,0,0,.82);z-index:999;align-items:center;justify-content:center;padding:20px;backdrop-filter:blur(6px);}
    .mbg.open{display:flex;}
    .modal{background:var(--dark2);border-radius:20px;max-width:720px;width:100%;display:grid;grid-template-columns:1fr 1fr;border:1px solid rgba(255,255,255,.08);overflow:hidden;max-height:90vh;}
    .mimg{width:100%;aspect-ratio:1;object-fit:cover;}
    .mbody{padding:36px;overflow-y:auto;}
    /* CART */
    .ci{display:flex;gap:16px;background:var(--dark2);border-radius:16px;padding:16px;border:1px solid rgba(255,255,255,.06);margin-bottom:16px;}
    .ci img{width:80px;height:80px;border-radius:10px;object-fit:cover;background:var(--dark3);}
    .qctrl{display:flex;align-items:center;gap:10px;background:var(--dark3);border-radius:8px;padding:4px 12px;}
    .qbtn{background:none;border:none;color:var(--text);cursor:pointer;font-size:18px;line-height:1;}
    /* ADMIN */
    .astats{display:grid;grid-template-columns:repeat(3,1fr);gap:16px;margin-bottom:36px;max-width:500px;}
    .asb{background:var(--dark2);border-radius:12px;padding:20px;text-align:center;border:1px solid rgba(201,168,76,.12);}
    .asv{font-family:'Playfair Display',serif;font-size:28px;font-weight:700;color:var(--gold);}
    .asl{font-size:11px;color:var(--muted);letter-spacing:1px;text-transform:uppercase;margin-top:4px;}
    .agrid{display:grid;grid-template-columns:1fr 1.3fr;gap:32px;}
    .panel{background:var(--dark2);border-radius:20px;padding:32px;border:1px solid rgba(255,255,255,.06);}
    .pt{font-family:'Playfair Display',serif;font-size:22px;font-weight:700;color:var(--gold);margin-bottom:24px;}
    .fld{margin-bottom:16px;}
    .fld label{display:block;font-size:11px;letter-spacing:2px;text-transform:uppercase;color:var(--muted);margin-bottom:6px;}
    .fld input,.fld select,.fld textarea{width:100%;background:var(--dark3);border:1px solid rgba(255,255,255,.1);border-radius:10px;padding:12px 16px;color:var(--text);font-family:'DM Sans',sans-serif;font-size:14px;}
    .fld input:focus,.fld select:focus,.fld textarea:focus{outline:none;border-color:var(--gold);}
    .fld textarea{resize:vertical;min-height:70px;}
    select option{background:var(--dark3);}
    .frow{display:grid;grid-template-columns:1fr 1fr;gap:12px;}
    .trow{display:flex;align-items:center;justify-content:space-between;background:var(--dark3);border-radius:10px;padding:12px 16px;margin-bottom:10px;cursor:pointer;}
    .ttrack{width:44px;height:24px;border-radius:50px;position:relative;transition:background .3s;}
    .tthumb{position:absolute;width:18px;height:18px;background:#fff;border-radius:50%;top:3px;transition:left .3s;}
    .apl{display:flex;flex-direction:column;gap:12px;max-height:68vh;overflow-y:auto;padding-right:4px;}
    .api{display:flex;gap:14px;background:var(--dark3);border-radius:12px;padding:14px;border:1px solid rgba(255,255,255,.04);}
    .apt{width:64px;height:64px;border-radius:8px;object-fit:cover;background:var(--dark);}
    .cpill{display:inline-block;padding:2px 10px;border-radius:50px;font-size:10px;font-weight:700;letter-spacing:1px;text-transform:uppercase;}
    .cc{background:rgba(59,130,246,.2);color:#60a5fa;}
    .cs2{background:rgba(34,197,94,.2);color:#4ade80;}
    .cj{background:rgba(201,168,76,.2);color:var(--gold);}
    .bedit{background:rgba(201,168,76,.1);border:1px solid rgba(201,168,76,.3);color:var(--gold);padding:6px 12px;border-radius:6px;font-size:12px;cursor:pointer;font-family:'DM Sans',sans-serif;}
    .bdel{background:rgba(230,57,70,.1);border:1px solid rgba(230,57,70,.3);color:var(--accent);padding:6px 12px;border-radius:6px;font-size:12px;cursor:pointer;font-family:'DM Sans',sans-serif;}
    /* TOAST */
    .toast{position:fixed;bottom:32px;right:32px;color:#fff;padding:14px 24px;border-radius:12px;font-weight:700;font-size:14px;z-index:9999;opacity:0;transform:translateY(20px);transition:all .3s;pointer-events:none;}
    .toast.show{opacity:1;transform:translateY(0);}
    .loader{display:flex;justify-content:center;padding:80px 0;}
    .spinner{width:40px;height:40px;border:3px solid rgba(201,168,76,.2);border-top:3px solid var(--gold);border-radius:50%;animation:spin .8s linear infinite;}
    footer{background:var(--dark2);border-top:1px solid rgba(255,255,255,.06);padding:48px 5% 24px;}
    .fg{display:grid;grid-template-columns:2fr 1fr 1fr;gap:40px;margin-bottom:40px;}
    .fl{font-family:'Playfair Display',serif;font-size:24px;font-weight:700;color:var(--gold);margin-bottom:12px;}
    .fh{font-size:11px;letter-spacing:3px;text-transform:uppercase;color:var(--gold);margin-bottom:16px;}
    .fb{border-top:1px solid rgba(255,255,255,.06);padding-top:20px;text-align:center;color:var(--muted);font-size:13px;}
    @media(max-width:768px){
      .cat-grid{grid-template-columns:1fr 1fr;}.cat-card:last-child{grid-column:span 2;}
      .agrid{grid-template-columns:1fr;}.modal{grid-template-columns:1fr;}
      .mimg{height:220px;aspect-ratio:auto;}.fg{grid-template-columns:1fr;}
      .hero-stats{gap:20px;}.stores-g{grid-template-columns:1fr;}
      .nav-links{gap:12px;}
    }
  </style>
</head>
<body>
<nav>
  <div class="nav-inner">
    <div class="logo" onclick="showPage('home')">
      <div class="logo-box">GNR</div>
      <span class="logo-name">GNR Footwear</span>
    </div>
    <div class="nav-links">
      <button class="nav-btn" onclick="showPage('home')">Home</button>
      <button class="nav-btn" onclick="showPage('products')">Products</button>
      <button class="nav-btn" onclick="showPage('admin')">⚙ Admin</button>
      <button class="nav-cart" onclick="showPage('cart')">
        🛒 Cart <span class="cbadge" id="cb">0</span>
      </button>
    </div>
  </div>
</nav>

<!-- HOME -->
<div id="page-home" class="page active">
  <section class="hero">
    <div class="hero-c">
      <div class="h-badge">✦ New Collection 2026</div>
      <h1>Style that<br/><span>Defines</span> You</h1>
      <p>Bhadrachalam's favourite footwear &amp; jewellery store.</p>
      <div class="hero-btns">
        <button class="btn-p" onclick="showPage('products')">Shop Now →</button>
        <button class="btn-o" onclick="showPage('products');setFilter('crocs')">Browse Crocs</button>
      </div>
    </div>
    <div class="hero-stats">
      <div><div class="snum" id="hTotal">0</div><div class="slbl">Products</div></div>
      <div><div class="snum">500+</div><div class="slbl">Customers</div></div>
      <div><div class="snum">2</div><div class="slbl">Stores</div></div>
    </div>
  </section>
  <div class="strip"><div class="strip-i">
    <span class="si">✦ FREE DELIVERY</span><span class="si">✦ EASY EXCHANGE</span><span class="si">✦ LATEST CROCS</span>
    <span class="si">✦ PREMIUM JEWELLERY</span><span class="si">✦ BEST PRICES</span><span class="si">✦ GNR FOOTWEAR</span>
    <span class="si">✦ FREE DELIVERY</span><span class="si">✦ EASY EXCHANGE</span><span class="si">✦ LATEST CROCS</span>
    <span class="si">✦ PREMIUM JEWELLERY</span><span class="si">✦ BEST PRICES</span><span class="si">✦ GNR FOOTWEAR</span>
  </div></div>
  <section class="sec" style="background:var(--dark2)">
    <div class="stag">✦ Shop By</div>
    <div class="stitle">Our <span>Collections</span></div>
    <div class="cat-grid">
      <div class="cat-card" onclick="showPage('products');setFilter('crocs')"><img src="https://images.unsplash.com/photo-1606107557195-0e29a4b5b4aa?w=600&q=80" alt="Crocs"/><div class="cat-ov"></div><div class="cat-info"><div class="cn">Crocs &amp; Flip Flops</div><div class="cs">✦ Trending</div><button class="cat-btn">Shop Now →</button></div></div>
      <div class="cat-card" onclick="showPage('products');setFilter('shoes')"><img src="https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=600&q=80" alt="Shoes"/><div class="cat-ov"></div><div class="cat-info"><div class="cn">Shoes</div><div class="cs">✦ Men &amp; Women</div><button class="cat-btn">Shop Now →</button></div></div>
      <div class="cat-card" onclick="showPage('products');setFilter('jewellery')"><img src="https://images.unsplash.com/photo-1515562141207-7a88fb7ce338?w=600&q=80" alt="Jewellery"/><div class="cat-ov"></div><div class="cat-info"><div class="cn">Jewellery</div><div class="cs">✦ Premium</div><button class="cat-btn">Shop Now →</button></div></div>
    </div>
  </section>
  <section class="sec">
    <div class="stag">✦ Fresh Stock</div>
    <div style="display:flex;justify-content:space-between;align-items:flex-end;margin-bottom:40px">
      <div class="stitle" style="margin-bottom:0">New <span>Arrivals</span></div>
      <button class="btn-o" style="padding:10px 24px;font-size:13px" onclick="showPage('products')">View All →</button>
    </div>
    <div class="pgrid" id="homeNew"><div class="loader"><div class="spinner"></div></div></div>
  </section>
  <div class="sale-b">
    <div class="stag" style="display:block;text-align:center">✦ Limited Time</div>
    <h2>🔥 SALE UP TO <span>50% OFF</span></h2>
    <p style="color:var(--muted);margin-bottom:28px;font-size:16px">New stock added regularly!</p>
    <div class="cdwn">
      <div class="cdb"><div class="cdn" id="cdH">00</div><div class="cdl">Hours</div></div>
      <div class="cdb"><div class="cdn" id="cdM">00</div><div class="cdl">Mins</div></div>
      <div class="cdb"><div class="cdn" id="cdS">00</div><div class="cdl">Secs</div></div>
    </div>
    <button class="btn-p" onclick="showPage('products')">Grab Deals →</button>
  </div>
  <section class="sec" style="background:var(--dark2)">
    <div class="stag">✦ Visit Us</div>
    <div class="stitle">Our <span>Stores</span></div>
    <div class="stores-g">
      <div class="store-c"><div class="store-t">GNR Footwear 1</div><div style="color:var(--muted);font-size:14px;line-height:1.7">📍 Beside Kasam Shopping Mall, Bhadrachalam</div></div>
      <div class="store-c"><div class="store-t">GNR Footwear 2</div><div style="color:var(--muted);font-size:14px;line-height:1.7">📍 Beside Apollo Pharmacy, UB Road, Bhadrachalam</div></div>
    </div>
  </section>
</div>

<!-- PRODUCTS -->
<div id="page-products" class="page">
  <div class="sec" style="padding-top:100px">
    <div class="stag">✦ Browse</div>
    <div class="stitle">All <span>Products</span></div>
    <div class="fltrs">
      <button class="fbtn active" onclick="setFilter('all',this)">All</button>
      <button class="fbtn" onclick="setFilter('crocs',this)">Crocs</button>
      <button class="fbtn" onclick="setFilter('shoes',this)">Shoes</button>
      <button class="fbtn" onclick="setFilter('jewellery',this)">Jewellery</button>
    </div>
    <div class="pgrid" id="allGrid"><div class="loader"><div class="spinner"></div></div></div>
  </div>
</div>

<!-- CART -->
<div id="page-cart" class="page">
  <div class="sec" style="padding-top:100px;max-width:720px;margin:0 auto">
    <div class="stitle">Your <span>Cart</span></div>
    <div id="cartDiv"></div>
  </div>
</div>

<!-- ADMIN -->
<div id="page-admin" class="page">
  <div class="sec" style="padding-top:100px">
    <div style="display:flex;align-items:center;gap:16px;margin-bottom:36px">
      <div style="font-family:'Playfair Display',serif;font-size:32px;font-weight:700">⚙ <span style="color:var(--gold)">Admin Panel</span></div>
      <span style="background:rgba(201,168,76,.15);border:1px solid var(--gold);color:var(--gold);padding:4px 14px;border-radius:50px;font-size:11px;letter-spacing:2px">OWNER ACCESS</span>
    </div>
    <div class="astats">
      <div class="asb"><div class="asv" id="aT">0</div><div class="asl">Products</div></div>
      <div class="asb"><div class="asv" id="aS">0</div><div class="asl">In Stock</div></div>
      <div class="asb"><div class="asv">3</div><div class="asl">Categories</div></div>
    </div>
    <div class="agrid">
      <div class="panel">
        <div class="pt" id="ftitle">➕ Add New Product</div>
        <div class="fld"><label>Product Name</label><input id="fN" placeholder="e.g. Classic Crocs Clog"/></div>
        <div class="fld"><label>Category</label>
          <select id="fC"><option value="crocs">Crocs / Flip Flops</option><option value="shoes">Shoes</option><option value="jewellery">Jewellery</option></select>
        </div>
        <div class="frow">
          <div class="fld"><label>Selling Price (₹)</label><input id="fP" type="number" placeholder="799" oninput="aDisc()"/></div>
          <div class="fld"><label>Original Price (₹)</label><input id="fO" type="number" placeholder="1299" oninput="aDisc()"/></div>
        </div>
        <div class="fld"><label>Discount %</label><input id="fD" type="number" placeholder="Auto-calculated"/></div>
        <div class="fld"><label>Image URL</label><input id="fI" type="url" placeholder="https://..." oninput="prevImg()"/></div>
        <img id="ipr" src="" style="display:none;width:100%;aspect-ratio:1;object-fit:cover;border-radius:10px;margin-bottom:16px"/>
        <div class="fld"><label>Description</label><textarea id="fDe" rows="3" placeholder="Describe the product..."></textarea></div>
        <div class="fld"><label>Extra Details</label><textarea id="fEx" rows="2" placeholder="Delivery, care instructions..."></textarea></div>
        <div class="trow" onclick="tog('tN')">
          <span>🆕 Mark as New Arrival</span>
          <div class="ttrack" id="tr-tN" style="background:var(--gold)"><div class="tthumb" id="th-tN" style="left:23px"></div></div>
        </div>
        <div class="trow" onclick="tog('tS')">
          <span>✅ In Stock</span>
          <div class="ttrack" id="tr-tS" style="background:var(--gold)"><div class="tthumb" id="th-tS" style="left:23px"></div></div>
        </div>
        <button class="btn-p" style="width:100%;margin-top:20px" id="sbtn" onclick="submitProd()">➕ Add Product to Store</button>
        <button id="cbtn" style="display:none;width:100%;background:transparent;border:1px solid rgba(255,255,255,.12);color:var(--muted);padding:12px;border-radius:10px;font-size:14px;cursor:pointer;font-family:'DM Sans',sans-serif;margin-top:8px" onclick="cancelEdit()">✕ Cancel</button>
      </div>
      <div class="panel">
        <div class="pt">📦 All Products</div>
        <div class="apl" id="apl"></div>
      </div>
    </div>
  </div>
</div>

<!-- MODAL -->
<div class="mbg" id="mbg" onclick="if(event.target===this)this.classList.remove('open')">
  <div class="modal">
    <img class="mimg" id="mi" src="" alt=""/>
    <div class="mbody">
      <div style="font-size:11px;letter-spacing:3px;text-transform:uppercase;color:var(--gold);margin-bottom:8px" id="mc"></div>
      <div style="font-family:'Playfair Display',serif;font-size:26px;font-weight:700;margin-bottom:12px;line-height:1.2" id="mn"></div>
      <div style="color:var(--muted);font-size:14px;line-height:1.7;margin-bottom:14px" id="md"></div>
      <div style="color:var(--muted);font-size:13px;line-height:1.6;border-top:1px solid rgba(255,255,255,.08);padding-top:14px;margin-bottom:14px" id="me"></div>
      <div style="font-family:'Playfair Display',serif;font-size:30px;font-weight:700;color:var(--gold)" id="mp"></div>
      <div style="font-size:14px;color:var(--muted);text-decoration:line-through;margin-bottom:20px" id="mo"></div>
      <button class="btn-p" style="width:100%" onclick="addFromModal()">Add to Cart</button>
      <button class="btn-o" style="width:100%;margin-top:8px" onclick="document.getElementById('mbg').classList.remove('open')">Close</button>
    </div>
  </div>
</div>

<div class="toast" id="toast"></div>

<footer>
  <div class="fg">
    <div><div class="fl">GNR Footwear</div><p style="color:var(--muted);font-size:14px;line-height:1.7;max-width:280px">Premium Crocs, Shoes &amp; Jewellery — Bhadrachalam's favourite store.</p></div>
    <div><div class="fh">Categories</div><div style="color:var(--muted);font-size:14px;line-height:2">Crocs<br/>Shoes<br/>Jewellery</div></div>
    <div><div class="fh">Our Stores</div>
      <div style="color:var(--muted);font-size:13px;line-height:1.7;margin-bottom:12px">📍 GNR Footwear 1<br/>Beside Kasam Shopping Mall,<br/>Bhadrachalam</div>
      <div style="color:var(--muted);font-size:13px;line-height:1.7">📍 GNR Footwear 2<br/>Beside Apollo Pharmacy,<br/>UB Road, Bhadrachalam</div>
    </div>
  </div>
  <div class="fb">© 2026 GNR Footwear, Bhadrachalam. All rights reserved.</div>
</footer>

<script>
let products=[], cart=JSON.parse(localStorage.getItem('gnr_c')||'[]');
let curFilter='all', editId=null, modalP=null;
let togs={tN:true,tS:true};

async function load(){
  try{
    const r=await fetch('/api/products'); products=await r.json();
    renderHome();renderAll();renderApl();updStats();
    document.getElementById('hTotal').textContent=products.length;
  }catch(e){toast('Cannot connect to server!','#E63946');}
}

function showPage(n){
  document.querySelectorAll('.page').forEach(p=>p.classList.remove('active'));
  document.getElementById('page-'+n).classList.add('active');
  window.scrollTo({top:0,behavior:'smooth'});
  if(n==='cart')renderCart();
  if(n==='admin'){renderApl();updStats();}
}

function pcard(p){
  return `<div class="pcard" onclick="openM(${p.id})">
    <div class="pimgw">
      <img src="${p.image||'https://via.placeholder.com/300/242424/888?text=GNR'}" alt="${p.name}" onerror="this.src='https://via.placeholder.com/300/242424/888?text=GNR'"/>
      ${p.discount>0?`<span class="bdg bdg-d">-${p.discount}%</span>`:''}
      ${p.is_new===1?`<span class="bdg bdg-n">NEW</span>`:''}
      ${p.in_stock===0?`<div class="bdg-oos">OUT OF STOCK</div>`:''}
    </div>
    <div class="pbody">
      <div class="pclbl">${p.category}</div>
      <div class="pname">${p.name}</div>
      <div class="pprices">
        <span class="pprice">&#8377;${p.price}</span>
        ${p.original_price>0?`<span class="porig">&#8377;${p.original_price}</span>`:''}
        ${p.discount>0?`<span class="psave">Save ${p.discount}%</span>`:''}
      </div>
      <div class="pactions">
        <button class="bcart" id="bc${p.id}" onclick="event.stopPropagation();addC(${p.id})" ${p.in_stock===0?'disabled style="opacity:.5;cursor:not-allowed"':''}>Add to Cart</button>
        <button class="bwish" onclick="event.stopPropagation()">&#9825;</button>
      </div>
    </div>
  </div>`;
}

function renderHome(){
  const el=document.getElementById('homeNew');
  const it=products.filter(p=>p.is_new===1).slice(0,4);
  el.innerHTML=it.length?it.map(pcard).join(''):'<p style="color:var(--muted)">No new arrivals yet.</p>';
}

function renderAll(){
  const el=document.getElementById('allGrid');
  const it=curFilter==='all'?products:products.filter(p=>p.category===curFilter);
  el.innerHTML=it.length?it.map(pcard).join(''):'<p style="color:var(--muted);padding:60px 0;text-align:center;grid-column:1/-1">No products in this category yet.</p>';
}

function setFilter(cat,btn){
  curFilter=cat;
  document.querySelectorAll('.fbtn').forEach(b=>b.classList.remove('active'));
  if(btn)btn.classList.add('active');
  else document.querySelectorAll('.fbtn').forEach(b=>{if(b.textContent.toLowerCase()===cat||(cat==='all'&&b.textContent==='All'))b.classList.add('active');});
  renderAll();
}

function openM(id){
  const p=products.find(x=>x.id===id);if(!p)return;modalP=p;
  document.getElementById('mi').src=p.image||'https://via.placeholder.com/300/242424/888?text=GNR';
  document.getElementById('mc').textContent=p.category.toUpperCase();
  document.getElementById('mn').textContent=p.name;
  document.getElementById('md').textContent=p.description||'';
  const me=document.getElementById('me');
  me.textContent=p.extra||'';me.style.display=p.extra?'block':'none';
  document.getElementById('mp').textContent='&#8377;'+p.price;
  document.getElementById('mo').textContent=p.original_price>0?'Original: &#8377;'+p.original_price:'';
  document.getElementById('mbg').classList.add('open');
}
function addFromModal(){if(modalP)addC(modalP.id);document.getElementById('mbg').classList.remove('open');}

function addC(id){
  const p=products.find(x=>x.id===id);if(!p||p.in_stock===0)return;
  const ex=cart.find(i=>i.id===id);
  if(ex)ex.qty++;else cart.push({...p,qty:1});
  saveC();updBadge();
  const b=document.getElementById('bc'+id);
  if(b){const o=b.textContent;b.textContent='✓ Added!';b.classList.add('added');setTimeout(()=>{b.textContent=o;b.classList.remove('added');},1300);}
  toast('✓ '+p.name+' added!');
}

function saveC(){localStorage.setItem('gnr_c',JSON.stringify(cart));}
function updBadge(){
  const n=cart.reduce((s,i)=>s+i.qty,0);
  const b=document.getElementById('cb');b.textContent=n;b.style.display=n>0?'flex':'none';
}

function renderCart(){
  const el=document.getElementById('cartDiv');
  if(!cart.length){el.innerHTML=`<div style="text-align:center;padding:80px 0"><div style="font-size:48px;margin-bottom:16px">🛒</div><div style="color:var(--muted);font-size:16px;margin-bottom:24px">Your cart is empty</div><button class="btn-p" onclick="showPage('products')">Browse Products →</button></div>`;return;}
  const total=cart.reduce((s,i)=>s+(i.price*i.qty),0);
  el.innerHTML=cart.map(i=>`<div class="ci"><img src="${i.image||''}" alt="${i.name}" onerror="this.src='https://via.placeholder.com/80/242424/888?text=GNR'"/>
    <div style="flex:1"><div style="font-weight:600;margin-bottom:4px">${i.name}</div><div style="font-size:12px;color:var(--muted);text-transform:uppercase;letter-spacing:1px;margin-bottom:8px">${i.category}</div><div style="color:var(--gold);font-weight:700">&#8377;${i.price*i.qty}</div></div>
    <div style="display:flex;flex-direction:column;align-items:center;gap:8px">
      <div class="qctrl"><button class="qbtn" onclick="chQ(${i.id},-1)">&#8722;</button><span style="font-size:14px;font-weight:600;min-width:20px;text-align:center">${i.qty}</span><button class="qbtn" onclick="chQ(${i.id},1)">+</button></div>
      <button onclick="remC(${i.id})" style="background:none;border:none;color:var(--accent);cursor:pointer;font-size:12px">Remove</button>
    </div></div>`).join('')+
  `<div style="background:var(--dark2);border-radius:16px;padding:28px;border:1px solid rgba(255,255,255,.08)">
    <div style="display:flex;justify-content:space-between;font-size:18px;font-weight:700;margin-bottom:20px"><span>Total</span><span style="color:var(--gold)">&#8377;${total}</span></div>
    <button class="btn-p" style="width:100%" onclick="waOrder()">📲 Order via WhatsApp</button>
    <button class="btn-o" style="width:100%;margin-top:8px" onclick="cart=[];saveC();updBadge();renderCart()">Clear Cart</button>
  </div>`;
}

function chQ(id,d){const i=cart.find(x=>x.id===id);if(i){i.qty=Math.max(1,i.qty+d);saveC();updBadge();renderCart();}}
function remC(id){cart=cart.filter(i=>i.id!==id);saveC();updBadge();renderCart();}
function waOrder(){
  const t=cart.reduce((s,i)=>s+(i.price*i.qty),0);
  const m=encodeURIComponent('Hello GNR Footwear! I want to order:\n'+cart.map(i=>`${i.name} x${i.qty} - Rs.${i.price*i.qty}`).join('\n')+'\n\nTotal: Rs.'+t);
  window.open('https://wa.me/91XXXXXXXXXX?text='+m,'_blank');
}

// ADMIN
function tog(k){togs[k]=!togs[k];document.getElementById('tr-'+k).style.background=togs[k]?'var(--gold)':'#333';document.getElementById('th-'+k).style.left=togs[k]?'23px':'3px';}
function aDisc(){const p=parseFloat(document.getElementById('fP').value),o=parseFloat(document.getElementById('fO').value);if(p&&o&&o>p)document.getElementById('fD').value=Math.round((1-p/o)*100);}
function prevImg(){const u=document.getElementById('fI').value,img=document.getElementById('ipr');if(u){img.src=u;img.style.display='block';img.onerror=()=>img.style.display='none';}else img.style.display='none';}
function gForm(){return{name:document.getElementById('fN').value.trim(),category:document.getElementById('fC').value,price:parseFloat(document.getElementById('fP').value)||0,original_price:parseFloat(document.getElementById('fO').value)||0,discount:parseInt(document.getElementById('fD').value)||0,image:document.getElementById('fI').value.trim(),description:document.getElementById('fDe').value.trim(),extra:document.getElementById('fEx').value.trim(),is_new:togs.tN,in_stock:togs.tS};}
function fillF(p){document.getElementById('fN').value=p.name;document.getElementById('fC').value=p.category;document.getElementById('fP').value=p.price;document.getElementById('fO').value=p.original_price||'';document.getElementById('fD').value=p.discount||'';document.getElementById('fI').value=p.image||'';prevImg();document.getElementById('fDe').value=p.description||'';document.getElementById('fEx').value=p.extra||'';togs.tN=p.is_new===1;togs.tS=p.in_stock!==0;['tN','tS'].forEach(k=>{document.getElementById('tr-'+k).style.background=togs[k]?'var(--gold)':'#333';document.getElementById('th-'+k).style.left=togs[k]?'23px':'3px';});}
function clrF(){['fN','fP','fO','fD','fI','fDe','fEx'].forEach(id=>document.getElementById(id).value='');document.getElementById('fC').value='crocs';document.getElementById('ipr').style.display='none';togs={tN:true,tS:true};['tN','tS'].forEach(k=>{document.getElementById('tr-'+k).style.background='var(--gold)';document.getElementById('th-'+k).style.left='23px';});}

async function submitProd(){
  const d=gForm();
  if(!d.name){toast('Enter product name!','#E63946');return;}
  if(!d.price){toast('Enter price!','#E63946');return;}
  document.getElementById('sbtn').textContent='⏳ Saving...';
  try{
    let u;
    if(editId){const r=await fetch('/api/products/'+editId,{method:'PUT',headers:{'Content-Type':'application/json'},body:JSON.stringify(d)});u=await r.json();products=products.map(p=>p.id===editId?u:p);toast('✅ Product updated!');}
    else{const r=await fetch('/api/products',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(d)});u=await r.json();products=[u,...products];toast('🎉 Added to store!');}
    clrF();cancelEdit();renderHome();renderAll();renderApl();updStats();
    document.getElementById('hTotal').textContent=products.length;
  }catch(e){toast('Error! Is server running?','#E63946');}
  document.getElementById('sbtn').textContent=editId?'💾 Save Changes':'➕ Add Product to Store';
}

function editProd(id){const p=products.find(x=>x.id===id);if(!p)return;editId=id;fillF(p);document.getElementById('ftitle').textContent='✏️ Edit Product';document.getElementById('sbtn').textContent='💾 Save Changes';document.getElementById('cbtn').style.display='block';window.scrollTo({top:0,behavior:'smooth'});}
function cancelEdit(){editId=null;clrF();document.getElementById('ftitle').textContent='➕ Add New Product';document.getElementById('sbtn').textContent='➕ Add Product to Store';document.getElementById('cbtn').style.display='none';}

async function delProd(id){
  if(!confirm('Delete this product?'))return;
  await fetch('/api/products/'+id,{method:'DELETE'});
  products=products.filter(p=>p.id!==id);
  renderHome();renderAll();renderApl();updStats();
  document.getElementById('hTotal').textContent=products.length;
  toast('🗑 Deleted','#E63946');
}

function renderApl(){
  const el=document.getElementById('apl');
  if(!products.length){el.innerHTML='<p style="color:var(--muted);text-align:center;padding:40px 0">No products yet.</p>';return;}
  el.innerHTML=products.map(p=>`<div class="api">
    <img class="apt" src="${p.image||''}" alt="${p.name}" onerror="this.src='https://via.placeholder.com/64/242424/888?text=GNR'"/>
    <div style="flex:1">
      <div style="font-weight:600;font-size:14px;margin-bottom:4px">${p.name}</div>
      <div style="display:flex;gap:6px;align-items:center;margin-bottom:4px">
        <span class="cpill ${p.category==='crocs'?'cc':p.category==='shoes'?'cs2':'cj'}">${p.category}</span>
        ${p.is_new===1?'<span style="font-size:10px;color:var(--gold)">✦ NEW</span>':''}
        ${p.in_stock===0?'<span style="font-size:10px;color:var(--accent)">OUT OF STOCK</span>':''}
      </div>
      <div style="color:var(--gold);font-weight:700;font-size:15px">&#8377;${p.price} <span style="color:var(--muted);font-size:12px;font-weight:400;text-decoration:line-through">${p.original_price>0?'&#8377;'+p.original_price:''}</span></div>
    </div>
    <div style="display:flex;flex-direction:column;gap:6px">
      <button class="bedit" onclick="editProd(${p.id})">✏️ Edit</button>
      <button class="bdel" onclick="delProd(${p.id})">🗑 Del</button>
    </div>
  </div>`).join('');
}

async function updStats(){
  try{const s=await fetch('/api/stats').then(r=>r.json());document.getElementById('aT').textContent=s.total;document.getElementById('aS').textContent=s.in_stock;}catch{}
}

function startCd(){
  let e=parseInt(localStorage.getItem('gnr_s')||'0');
  if(!e||Date.now()>e){e=Date.now()+24*3600000;localStorage.setItem('gnr_s',e);}
  function t(){const d=Math.max(0,e-Date.now());document.getElementById('cdH').textContent=String(Math.floor(d/3600000)).padStart(2,'0');document.getElementById('cdM').textContent=String(Math.floor((d%3600000)/60000)).padStart(2,'0');document.getElementById('cdS').textContent=String(Math.floor((d%60000)/1000)).padStart(2,'0');}
  t();setInterval(t,1000);
}

function toast(msg,bg='#2d9e5f'){const t=document.getElementById('toast');t.textContent=msg;t.style.background=bg;t.classList.add('show');setTimeout(()=>t.classList.remove('show'),2500);}

updBadge();startCd();load();
</script>
</body>
</html>"""

if __name__ == '__main__':
    init_db()
    print("\n" + "="*52)
    print("  ✅  GNR Footwear Store is RUNNING!")
    print("  🌐  Open in browser: http://127.0.0.1:5000")
    print("  ⚙   Admin panel:    http://127.0.0.1:5000 → Admin")
    print("="*52 + "\n")
    app.run(debug=True, port=5000, host='0.0.0.0')
