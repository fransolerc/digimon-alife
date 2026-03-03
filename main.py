# main.py
from flask import Flask, request, jsonify
from agent.digimon import Digimon
from config import PORT

app = Flask(__name__)
agumon = Digimon()

@app.route('/state', methods=['POST'])
def receive_state():
    data = request.get_json()
    response = agumon.process(data)
    return jsonify(response)

if __name__ == '__main__':
    app.run(port=PORT)