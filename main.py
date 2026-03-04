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

@app.route('/status', methods=['GET'])
def get_status():
    return jsonify({
        "hunger": round(agumon.hunger, 1),
        "energy": round(agumon.energy, 1),
        "curiosity": round(agumon.curiosity, 1),
        "cycle": agumon.memory.cycle_count,
        "recent_targets": agumon.memory.recent_targets,
        "processing": agumon.processing
    })

if __name__ == '__main__':
    app.run(port=PORT)