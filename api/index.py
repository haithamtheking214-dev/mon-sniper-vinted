from flask import Flask, render_template_string, request, jsonify
import requests
import time

app = Flask(__name__)

class VintedEngine:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
            'Accept-Language': 'fr-FR,fr;q=0.9',
        }

    def fetch_items(self, q, pmin, pmax, status):
        session = requests.Session()
        try:
            # Bypass simple des cookies
            session.get("https://www.vinted.fr", headers=self.headers, timeout=10)
            url = f"https://www.vinted.fr/api/v2/catalog/items?search_text={q}&order=newest_first"
            if pmin: url += f"&price_from={pmin}"
            if pmax: url += f"&price_to={pmax}"
            if status: url += f"&status_ids={status}"
            
            r = session.get(url, headers=self.headers, timeout=10)
            if r.status_code == 200:
                return r.json().get('items', [])
            return {"error": f"Vinted Status {r.status_code}"}
        except Exception as e:
            return {"error": str(e)}

engine = VintedEngine()

HTML_PRO = """
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <script src="https://cdn.tailwindcss.com"></script>
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.0/css/all.min.css" rel="stylesheet">
    <style>
        body { background: #020202; color: #fff; font-family: 'Inter', sans-serif; display: flex; height: 100vh; overflow: hidden; }
        .sidebar { width: 300px; background: #080808; border-right: 1px solid #151515; padding: 30px; display: flex; flex-direction: column; }
        .accent { color: #00e1ff; text-shadow: 0 0 10px rgba(0, 225, 255, 0.3); }
        .bg-accent { background: #00e1ff; }
        .panel { background: #0a0a0a; border: 1px solid #151515; border-radius: 15px; }
        .item-card { background: #0d0d0d; border: 1px solid #1a1a1a; transition: 0.3s cubic-bezier(0.4, 0, 0.2, 1); border-radius: 12px; }
        .item-card:hover { border-color: #00e1ff; transform: translateY(-5px); box-shadow: 0 10px 30px rgba(0,0,0,0.5); }
        input, select { background: #000 !important; border: 1px solid #222 !important; color: white !important; font-size: 13px !important; }
        input:focus { border-color: #00e1ff !important; outline: none; }
        .nav-link { color: #555; padding: 12px; border-radius: 8px; transition: 0.2s; display: flex; align-items: center; gap: 10px; font-size: 14px; }
        .nav-link.active { background: rgba(0, 225, 255, 0.05); color: #00e1ff; }
        ::-webkit-scrollbar { width: 5px; }
        ::-webkit-scrollbar-thumb { background: #222; border-radius: 10px; }
    </style>
</head>
<body>
    <div class="sidebar">
        <h1 class="text-3xl font-black italic accent mb-10 tracking-tighter uppercase">V-SNIPER</h1>
        <div class="space-y-2 flex-1">
            <div class="nav-link active"><i class="fas fa-search"></i> Sniper Live</div>
            <div class="nav-link"><i class="fas fa-bolt"></i> Auto-Buy <span class="text-[8px] bg-red-600 text-white px-1 rounded ml-auto">PRO</span></div>
            <div class="nav-link"><i class="fas fa-history"></i> Historique</div>
            <div class="nav-link"><i class="fas fa-cog"></i> Configuration</div>
        </div>
        <div class="mt-auto panel p-4">
            <p class="text-[10px] text-zinc-500 uppercase font-bold mb-2">Statut Système</p>
            <div class="flex items-center gap-2 text-[10px]">
                <div class="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
                VERCEL_CLOUD_ACTIVE
            </div>
        </div>
    </div>

    <div class="flex-1 flex flex-col">
        <header class="p-6 border-b border-zinc-900 bg-black/50 backdrop-blur-xl">
            <div class="max-w-5xl flex gap-4">
                <input id="q" placeholder="Recherche (ex: Nike Nocta)..." class="flex-1 p-3 rounded-xl">
                <input id="pmax" type="number" placeholder="Prix Max" class="w-28 p-3 rounded-xl">
                <select id="status" class="w-44 p-3 rounded-xl">
                    <option value="">Tous états</option>
                    <option value="6">Neuf avec étiquette</option>
                    <option value="1">Neuf</option>
                    <option value="2">Très bon état</option>
                </select>
                <button onclick="scan()" class="bg-accent text-black font-black px-10 py-3 rounded-xl uppercase hover:scale-105 transition active:scale-95">Scanner</button>
            </div>
        </header>

        <div id="grid" class="flex-1 overflow-y-auto p-10 grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-6">
            <div class="col-span-full text-center py-40 opacity-10">
                <i class="fas fa-satellite-dish text-8xl mb-6"></i>
                <h2 class="text-2xl font-bold uppercase tracking-widest">En attente de cible</h2>
            </div>
        </div>
    </div>

    <script>
        async function scan() {
            const grid = document.getElementById('grid');
            grid.innerHTML = '<div class="col-span-full text-center py-40"><p class="accent animate-bounce text-xl font-black uppercase tracking-widest">Scanning Vinted Network...</p></div>';
            
            const q = document.getElementById('q').value;
            const pmax = document.getElementById('pmax').value;
            const status = document.getElementById('status').value;
            
            try {
                const r = await fetch(`/api/scan?q=${q}&pmax=${pmax}&status=${status}`);
                const data = await r.json();
                
                if (data.error) {
                    grid.innerHTML = `<div class="col-span-full text-red-500 text-center p-10 panel">${data.error}</div>`;
                    return;
                }

                grid.innerHTML = data.map(i => `
                    <div class="item-card flex flex-col p-2">
                        <div class="relative rounded-xl overflow-hidden mb-3">
                            <img src="${i.photo?.url}" class="w-full h-52 object-cover">
                            <div class="absolute top-2 right-2 bg-black/90 px-3 py-1 rounded-lg text-xs font-black accent border border-accent/20">${i.price?.amount}€</div>
                        </div>
                        <div class="p-2 flex flex-col flex-1">
                            <p class="text-[9px] text-zinc-600 uppercase font-bold mb-1">${i.brand_title}</p>
                            <h3 class="text-xs truncate font-semibold text-zinc-300 mb-4">${i.title}</h3>
                            <a href="https://www.vinted.fr${i.url}" target="_blank" class="mt-auto block w-full bg-white text-black text-center py-2 rounded-lg font-black text-[10px] uppercase hover:bg-cyan-400 transition">Snipe Offer</a>
                        </div>
                    </div>
                `).join('');
            } catch(e) {
                grid.innerHTML = '<div class="col-span-full text-red-500 text-center p-10 panel">Erreur de connexion.</div>';
            }
        }
    </script>
</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(HTML_PRO)

@app.route('/api/scan')
def scan():
    q = request.args.get('q', 'Nike')
    pmax = request.args.get('pmax', '')
    status = request.args.get('status', '')
    items = engine.fetch_items(q, None, pmax, status)
    return jsonify(items if isinstance(items, list) else {"error": items.get('error')})

app = app