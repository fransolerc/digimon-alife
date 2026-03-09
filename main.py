from flask import Flask, request, jsonify
from agent.digimon import Digimon
from config import PORT
from agent.lore import generate_lore
from agent.perception import get_touching_from_spatial
from agent.needs import handle_touching

app = Flask(__name__)
agents = {}


def _get_or_create_agent(agent_id):
    if agent_id not in agents:
        name = agent_id.split("_")[0].capitalize()
        lore = generate_lore(name)
        agents[agent_id] = Digimon(agent_id, lore)
    return agents[agent_id]


def _require_id(data):
    agent_id = data.get("id")
    if not agent_id:
        return None, jsonify({"error": "missing agent id"}), 400
    return agent_id, None, None


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
    agent_id, err, code = _require_id(data)
    if err:
        return err, code
    agent = _get_or_create_agent(agent_id)
    agent.memory.update_spatial(data.get("detected", []))
    return jsonify({"status": "ok"})


@app.route('/think', methods=['POST'])
def think():
    data = request.json
    agent_id, err, code = _require_id(data)
    if err:
        return err, code
    agent = _get_or_create_agent(agent_id)
    return jsonify(agent.think_cycle(data))


@app.route('/move', methods=['POST'])
def move():
    data = request.json
    agent_id, err, code = _require_id(data)
    if err:
        return err, code
    if agent_id not in agents:
        return jsonify({"target_x": 0, "target_y": 0})
    return jsonify(agents[agent_id].move_cycle(data))


@app.route('/explored', methods=['POST'])
def explored():
    data = request.json
    agent_id, err, code = _require_id(data)
    if err:
        return err, code
    if agent_id not in agents:
        return jsonify({"status": "unknown agent"})
    agents[agent_id].memory.add_explored_zone(data.get("x", 0), data.get("y", 0))
    return jsonify({"status": "ok"})


@app.route('/position', methods=['POST'])
def position():
    data = request.json
    agent_id, err, code = _require_id(data)
    if err:
        return err, code
    agent = _get_or_create_agent(agent_id)
    agent.x = data.get("x", 0)
    agent.y = data.get("y", 0)
    touching = get_touching_from_spatial(agent.x, agent.y, agent.memory.spatial)
    handle_touching(agent, touching)
    agent.memory.save()
    return jsonify({"status": "ok", "touching": touching})


if __name__ == '__main__':
    app.run(port=PORT)