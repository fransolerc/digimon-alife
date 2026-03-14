from flask import Flask, request, jsonify, make_response
from agent.digimon import Digimon
from config import PORT
from agent.lore import generate_lore
from agent.perception import get_touching_from_spatial
from agent.needs import handle_touching

app = Flask(__name__)
agents = {}

def _cors(response):
    response.headers["Access-Control-Allow-Origin"] = "*"
    return response


@app.route('/debug/<agent_id>', methods=['GET'])
def debug_agent(agent_id):
    if agent_id not in agents:
        return _cors(make_response(jsonify({"error": "agent not found"}), 404))
    agent = agents[agent_id]
    data = {
        "x": agent.x,
        "y": agent.y,
        "hunger":    round(agent.hunger, 1),
        "energy":    round(agent.energy, 1),
        "curiosity": round(agent.curiosity, 1),
        "cycle":     agent.memory.cycle_count,
        "processing": agent.processing,
        "current_target": agent.current_target,
        "recent_targets": agent.memory.recent_targets,
        "entries":   agent.memory.entries[-10:],
        "reflections": agent.memory.reflections,
        "spatial":   {
            k: {"x": round(v["x"]), "y": round(v["y"])}
            for k, v in agent.memory.spatial.items()
        },
        "explored_zones_count": len(agent.memory.explored_zones),
        "associative_count": len(agent.memory.associative.nodes),
        "spatial_map": {
            "grid":    {f"{k[0]},{k[1]}": v for k, v in agent.memory.spatial_map.grid.items()},
            "objects": {f"{k[0]},{k[1]}": v for k, v in agent.memory.spatial_map.objects.items()}
        } if hasattr(agent.memory, "spatial_map") else {},
        "sim_clock": agent.memory.sim_clock.to_dict()
    }
    return _cors(make_response(jsonify(data), 200))


@app.route('/debug/<agent_id>', methods=['OPTIONS'])
def debug_options(_agent_id):
    resp = make_response("", 204)
    resp.headers["Access-Control-Allow-Origin"] = "*"
    resp.headers["Access-Control-Allow-Methods"] = "GET, OPTIONS"
    return resp

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
    pitch = data.get("pitch_rotation")
    return jsonify(agent.think_cycle(pitch_rotation=pitch))


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