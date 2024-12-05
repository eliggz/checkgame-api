from flask import Flask, request, jsonify
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)

@app.route('/checkgame', methods=['GET'])
def check_game():
    summoner_name = request.args.get('summoner_name')
    if not summoner_name:
        return jsonify({"error": "No summoner name provided."}), 400

    # Obtener lista de jugadores del torneo
    tournament_url = "https://soloboom.net/highelo"
    headers = {'User-Agent': 'Mozilla/5.0'}
    response = requests.get(tournament_url, headers=headers)
    if response.status_code != 200:
        return jsonify({"error": "No se pudo acceder a la lista de participantes."}), 500

    soup = BeautifulSoup(response.content, 'html.parser')
    tournament_players = [tag.text.strip() for tag in soup.find_all('div', class_='player-name')]

    # Scraping de op.gg
    opgg_url = f"https://www.op.gg/summoners/na/{summoner_name}"
    response = requests.get(opgg_url, headers=headers)
    if response.status_code != 200:
        return jsonify({"error": f"No se pudo acceder al perfil de {summoner_name} en op.gg."}), 500

    soup = BeautifulSoup(response.content, 'html.parser')
    live_game = soup.find('div', class_='live-game')
    if not live_game:
        return jsonify({"message": f"{summoner_name} no está en una partida en este momento."})

    players = [tag.text.strip() for tag in live_game.find_all('span', class_='summoner-name')]
    tournament_in_game = [player for player in players if player in tournament_players]

    if tournament_in_game:
        return jsonify({"message": f"{summoner_name} está en una partida con: {', '.join(tournament_in_game)}."})
    else:
        return jsonify({"message": f"{summoner_name} no está jugando con nadie del torneo."})

if __name__ == '__main__':
    app.run()
