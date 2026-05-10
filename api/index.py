from flask import Flask, render_template_string, request, jsonify
import requests

app = Flask(__name__)

def get_vinted_pro(q, pmin, pmax, size, status, sort):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept-Language': 'fr-FR,fr;q=0.9'
    }
    try:
        s = requests.Session()
        # Initialisation obligatoire pour les cookies
        s.get("https://www.vinted.fr", headers=headers, timeout=5)
        
        # Construction de l'URL avec TOUS les filtres
        params = f"search_text={q}&price_from={pmin}&price_to={pmax}&order={sort}"
        if size: params += f"&size_ids={size}"
        if status: params += f"&status_ids={status}"
        
        api_url = f"https://www.vinted.fr/api/v2/catalog/items?{params}&per_page=20"
        r = s.get(api_url, headers=headers, timeout=5)
        
        if r.status_code == 200:
            return [{
                "id": i.get('id'),
                "t": i.get('title'),
                "p": i.get('price', {}).get('amount'),
                "img": i.get('photo', {}).get('url'),
                "url": f"https://www.vinted.fr{i.get('url')}",
                "brand": i.get('brand_title'),
                "size": i.get('size_title')
            } for i in r.json().get('items', [])]
    except: pass
    return []

HTML = """
<!DOCTYPE html>
<html>
<head>
    <script src="https://cdn.tailwindcss.com"></script>
    <link href="https://fonts.googleapis.com/css2?family=Orbitron:wght@400;900&display=swap" rel="stylesheet">
    <style>
        body { background: #080808; color: #e5e7eb; font-family: 'Inter', sans-serif; }
        .v-tools-card { background: #111; border: 1px solid #222; transition: 0.2s; }
        .v-tools-card:hover { border-color: #00f2fe; box-shadow: 0 0 15px rgba(0,242,254,0.1); }
        .accent { color: #00f2fe; }
        .bg-accent { background: #00f2fe; }
        input, select { background: #181818 !important; border: 1px solid #333 !important; color: white !important; font-size: 12px !important; }
    </style>
</head>
<body class="p-6">
    <div class="max-w-7xl mx-auto">
        <div class="flex flex-col md:flex-row justify-between items-center mb-8 gap-4">
            <h1 style="font-family:'Orbitron'" class="text-3xl font-black italic accent uppercase tracking-tighter">V-TOOLS <span class="text-white">PRO</span></h1>
            
            <div class="grid grid-cols-2 md:grid-cols-6 gap-2 w-full md:w-auto">
                <input id="q" placeholder="Recherche..." class="p-2 rounded">
                <input id="pmin" type="number" placeholder="Prix Min" class="p-2 rounded">
                <input id="pmax" type="number" placeholder="Prix Max" class="p-2 rounded">
                <select id="status" class="p-2 rounded">
                    <option value="">État</option>
                    <option value="6">Neuf avec étiquette</option>
                    <option value="1">Neuf</option>
                    <option value="2">Très bon état</option>
                </select>
                <select id="sort" class="p-2 rounded">
                    <option value="newest_first">Plus récent</option>
                    <option value="price_low_to_high">Prix croissant</option>
                </select>
                <button onclick="scan()" class="bg-accent text-black font-black p-2 rounded hover:brightness-110 active:scale-95 transition uppercase text-xs">Scanner</button>
            </div>
        </div>

        <div id="loader" class="hidden h-1 bg-accent mb-4 animate-pulse"></div>
        <div id="grid" class="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-5 gap-4"></div>
    </div>

    <script>
        async function scan() {
            const grid = document.getElementById('grid');
            const loader = document.getElementById('loader');
            loader.classList.remove('hidden');
            
            const url = `/api/vtools?q=${document.getElementById('q').value}&pmin=${document.getElementById('pmin').value}&pmax=${document.getElementById('pmax').value}&status=${document.getElementById('status').value}&sort=${document.getElementById('sort').value}`;
            
            try {
                const r = await fetch(url);
                const data = await r.json();
                grid.innerHTML = data.map(i => `
                    <div class="v-tools-card rounded-lg overflow-hidden flex flex-col">
                        <div class="relative"><img src="${i.img}" class="w-full h-48 object-cover">
                        <div class="absolute bottom-0 left-0 bg-black/70 px-2 py-1 text-[10px] font-bold accent">${i.p}€</div></div>
                        <div class="p-3">
                            <p class="text-[9px] text-gray-500 uppercase font-bold">${i.brand} • ${i.size || 'N/A'}</p>
                            <h3 class="text-[11px] font-medium truncate my-1">${i.t}</h3>
                            <a href="${i.url}" target="_blank" class="block w-full bg-white text-black text-center py-2 rounded font-black text-[9px] mt-2 hover:bg-cyan-400 transition">SNIPE</a>
                        </div>
                    </div>
                `).join('');
            } catch(e) { alert("Erreur de connexion"); }
            loader.classList.add('hidden');
        }
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML)

@app.route('/api/vtools')
def api_vtools():
    q = request.args.get('q', '')
    pmin = request.args.get('pmin', '')
    pmax = request.args.get('pmax', '')
    status = request.args.get('status', '')
    sort = request.args.get('sort', 'newest_first')
    return jsonify(get_vinted_pro(q, pmin, pmax, None, status, sort))

app = app