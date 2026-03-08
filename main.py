from flask import Flask, request, jsonify
from agent.digimon import Digimon
from config import PORT
from agent.lore import generate_lore

app = Flask(__name__)
agents = {}

@app.route('/status', methods=['GET'])
def get_status():
    return jsonify({
        agent_id: {
            "hunger": round(agent.hunger, 1),
            "energy": round(agent.energy, 1),
            "curiosity": round(agent.curiosity, 1),
            "cycle": agent.memory.cycle_count,
            "recent_targets": agent.memory.recent_targets,
            "processing": agent.processing
        }
        for agent_id, agent in agents.items()
    })

@app.route('/perception', methods=['POST'])
def update_perception():
    data = request.json
    agent_id = data.get("id")
    if agent_id not in agents:
        name = agent_id.split("_")[0].capitalize()
        lore = generate_lore(name)
        agents[agent_id] = Digimon(agent_id, lore)
    detected = data.get("detected", [])
    agents[agent_id].memory.update_spatial(detected)
    return jsonify({"status": "ok"})

@app.route('/think', methods=['POST'])
def think():
    data = request.json
    agent_id = data.get("id")
    if agent_id not in agents:
        name = agent_id.split("_")[0].capitalize()
        lore = generate_lore(name)
        agents[agent_id] = Digimon(agent_id, lore)
    response = agents[agent_id].think_cycle(data)
    return jsonify(response)

@app.route('/move', methods=['POST'])
def move():
    data = request.json
    agent_id = data.get("id")
    if agent_id not in agents:
        return jsonify({"offset_x": 0, "offset_y": 0})
    response = agents[agent_id].move_cycle(data)
    return jsonify(response)

@app.route('/explored', methods=['POST'])
def explored():
    data = request.json
    agent_id = data.get("id")
    if agent_id not in agents:
        return jsonify({"status": "unknown agent"})
    x = data.get("x", 0)
    y = data.get("y", 0)
    agents[agent_id].memory.add_explored_zone(x, y)
    return jsonify({"status": "ok"})

if __name__ == '__main__':
    app.run(port=PORT)