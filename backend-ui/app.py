import requests
from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def home():
    api_message = "Pas de réponse"
    status_color = "danger"

    try:
        response = requests.get('http://api:5000/hello', timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            api_message = data.get('message', 'Erreur format')
            status_color = "success"
        else:
            api_message = f"Erreur API: {response.status_code}"

    except requests.exceptions.ConnectionError:
        api_message = "Impossible de contacter l'API (Est-elle lancée ?)"
    except Exception as e:
        api_message = f"Erreur grave : {str(e)}"

    context = {
        "titre": "Flask & Jinja",
        "message": api_message,
        "couleur_bouton": status_color,
        "items": [
            "Élément 1 généré par boucle Jinja",
            "Élément 2 généré par boucle Jinja",
            "Élément 3 généré par boucle Jinja"
        ]
    }
    return render_template('index.html', **context)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=80)