from flask import Flask, request, jsonify
from agent.digimon import Digimon
from config import PORT
from agent.lore import generate_lore

app = Flask(__name__)
agents = {}

@app.route('/state', methods=['POST'])
def receive_state():
    data = request.get_json()
    agent_id = data.get("id", "unknown")
    if agent_id not in agents:
        name = agent_id.split("_")[0].capitalize()
        lore = generate_lore(name)
        agents[agent_id] = Digimon(agent_id, lore)
    response = agents[agent_id].process(data)
    return jsonify(response)

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

    agent = agents[agent_id]
    nearby = data.get("nearby", [])
    x = data.get("x", agent.x)
    y = data.get("y", agent.y)
    agent.memory.update_spatial(x, y, nearby)
    agent.memory.save()

    return jsonify({"status": "ok"})

if __name__ == '__main__':
    app.run(port=PORT)