from flask import Flask, render_template_string
import requests

app = Flask(__name__)

headers = {
    "User-Agent": "Mozilla/5.0"
}

HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>V-Sniper</title>

    <style>
        body{
            background:#0b0f19;
            color:white;
            font-family:Arial;
            padding:40px;
        }

        h1{
            color:#3b82f6;
        }

        .card{
            background:#111827;
            padding:20px;
            border-radius:15px;
            margin-bottom:20px;
        }

        a{
            color:#60a5fa;
            text-decoration:none;
        }
    </style>
</head>
<body>

<h1>V-Sniper</h1>

{% for item in items %}
<div class="card">
    <h2>{{ item.title }}</h2>

    <p>Prix : {{ item.price }} €</p>

    <p>Marque : {{ item.brand_title }}</p>

    <a href="{{ item.url }}" target="_blank">
        Voir l'annonce
    </a>
</div>
{% endfor %}

</body>
</html>
"""


@app.route("/")
def home():

    url = "https://www.vinted.fr/api/v2/catalog/items"

    params = {
        "search_text": "Ralph Lauren",
        "price_to": 30,
        "order": "newest_first",
        "per_page": 20
    }

    response = requests.get(
        url,
        params=params,
        headers=headers
    )

    data = response.json()

    items = data.get("items", [])

    return render_template_string(
        HTML,
        items=items
    )


if __name__ == "__main__":
    app.run()