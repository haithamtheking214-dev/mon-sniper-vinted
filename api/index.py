from flask import Flask, render_template_string, request, jsonify
import requests

app = Flask(__name__)

# MOTEUR DE RECHERCHE VINTED
def get_vinted(query, pmax):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36'
    }
    try:
        session = requests.Session()
        # On simule une visite sur la home pour chopper les cookies
        session.get("https://www.vinted.fr", headers=headers, timeout=5)
        
        api_url = f"https://www.vinted.fr/api/v2/catalog/items?search_text={query}&price_to={pmax}&order=newest_first&per_page=12"
        r = session.get(api_url, headers=headers, timeout=5)
        
        if r.status_code == 200:
            items = r.json().get('items', [])
            return [{
                "title": i.get('title'),
                "price": i.get('price', {}).get('amount'),
                "img": i.get('photo', {}).get('url') if i.get('photo') else "",
                "url": f"https://www.vinted.fr{i.get('url')}",
                "brand": i.get('brand_title')
            } for i in items]
    except Exception as e:
        print(f"Erreur: {e}")
    return []

# INTERFACE NEON BLUE
UI_TEMPLATE = """
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <script src="https://cdn.tailwindcss.com"></script>
    <title>V-SNIPER CLOUD</title>
    <style>
        body { background: #050505; color: white; font-family: 'Inter', sans-serif; }
        .neon-border { border: 1px solid #00f2fe; box-shadow: 0 0 10px rgba(0, 242, 254, 0.2); }
        .cyan-text { color: #00f2fe; }
        .bg-cyan { background: #00f2fe; }
    </style>
</head>
<body class="p-4 md:p-10">
    <div class="max-w-6xl mx-auto">
        <header class="flex justify-between items-center mb-10">
            <h1 class="text-3xl font-black italic">V-SNIPER<span class="cyan-text">.</span></h1>
            <div class="flex gap-2">
                <input id="brand" placeholder="Marque..." class="bg-zinc-900 border border-zinc-800 p-2 rounded-lg outline-none focus:border-cyan-400 text-sm">
                <input id="price" type="number" placeholder="Prix Max" class="bg-zinc-900 border border-zinc-800 p-2 rounded-lg outline-none focus:border-cyan-400 text-sm w-24">
                <button onclick="startScan()" class="bg-cyan text-black font-bold px-4 py-2 rounded-lg text-sm hover:scale-105 transition">SCAN</button>
            </div>
        </header>

        <div id="loader" class="hidden text-center cyan-text animate-pulse mb-5">Recherche de pépites en cours...</div>
        
        <div id="grid" class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
            <!-- Les articles arrivent ici -->
        </div>
    </div>

    <script>
        async function startScan() {
            const b = document.getElementById('brand').value;
            const p = document.getElementById('price').value;
            const loader = document.getElementById('loader');
            const grid = document.getElementById('grid');

            if(!b) return alert("Choisis une marque !");
            
            loader.classList.remove('hidden');
            try {
                const r = await fetch(`/api/items?q=${b}&p=${p}`);
                const data = await r.json();
                
                grid.innerHTML = data.map(i => `
                    <div class="bg-zinc-900 rounded-xl overflow-hidden neon-border transition hover:-translate-y-1">
                        <img src="${i.img}" class="w-full h-48 object-cover">
                        <div class="p-4">
                            <p class="text-[10px] text-gray-500 uppercase">${i.brand}</p>
                            <h3 class="font-bold truncate text-sm mb-2">${i.title}</h3>
                            <div class="flex justify-between items-center">
                                <span class="cyan-text font-black">${i.price}€</span>
                                <a href="${i.url}" target="_blank" class="bg-white text-black text-[10px] px-3 py-1 rounded font-black uppercase">Voir</a>
                            </div>
                        </div>
                    </div>
                `).join('');
            } catch (e) {
                alert("Erreur lors du scan");
            }
            loader.classList.add('hidden');
        }
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(UI_TEMPLATE)

@app.route('/api/items')
def api_items():
    query = request.args.get('q', 'Nike')
    price = request.args.get('p', '100')
    items = get_vinted(query, price)
    return jsonify(items)

# TRES IMPORTANT POUR VERCEL
app = app
