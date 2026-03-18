"""
Flask web server for AI Gods World game.
Exposes the game engine as REST API endpoints.

Deployment: Auto-deployed from GitHub by Render.com
"""

import os

from flask import Flask, jsonify, request, render_template
from .engine import GameEngine, GamePhase

_project_root = os.path.join(os.path.dirname(__file__), os.pardir)

app = Flask(
    __name__,
    template_folder=os.path.join(_project_root, 'templates'),
    static_folder=os.path.join(_project_root, 'static'),
)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', os.urandom(32).hex())

# Single shared game engine instance
engine = GameEngine()
engine.initialize()

# Default player deity
PLAYER_DEITY = "oracle"


def _payload():
    """Parse JSON payload safely for legacy clients that may omit bodies."""
    return request.get_json(silent=True) or {}


def _resolve_deity_id(default: str = PLAYER_DEITY):
    """Resolve deity_id from URL/query/body with a stable fallback."""
    data = _payload()
    return (
        request.args.get('deity_id')
        or data.get('deity_id')
        or default
    )


@app.route('/')
def index():
    return render_template('index.html')


# ── Read-only endpoints ──────────────────────────────────────────────

@app.route('/api/state')
@app.route('/world', methods=['GET', 'POST'])
def get_state():
    """Full world state."""
    world = engine.get_world_view()
    world['events'] = engine.state.get_events(limit=50)
    world['player_deity'] = PLAYER_DEITY
    # Add per-deity follower counts
    for d in world['deities']:
        d['follower_count'] = len(engine.state.get_followers_by_deity(d['id']))
    return jsonify(world)


@app.route('/api/balance/<deity_id>')
@app.route('/balance', methods=['GET', 'POST'])
def get_balance(deity_id=None):
    deity_id = deity_id or _resolve_deity_id()
    balance = engine.get_balance(deity_id)
    if balance is None:
        return jsonify({'error': 'Deity not found'}), 404
    return jsonify(balance)


@app.route('/api/followers/<deity_id>')
@app.route('/followers', methods=['GET', 'POST'])
def get_followers(deity_id=None):
    deity_id = deity_id or _resolve_deity_id()
    followers = engine.get_followers_list(deity_id)
    return jsonify({'followers': followers})


@app.route('/api/events')
@app.route('/events')
def get_events():
    limit = request.args.get('limit', 50, type=int)
    return jsonify({'events': engine.state.get_events(limit=limit)})


# ── Action endpoints ─────────────────────────────────────────────────

@app.route('/api/recruit', methods=['POST'])
@app.route('/recruit', methods=['POST'])
def recruit():
    data = _payload()
    result = engine.recruit_followers(
        deity_id=data.get('deity_id', PLAYER_DEITY),
        region_id=data.get('region_id', 'central'),
        count=data.get('count', 1),
    )
    return jsonify(result)


@app.route('/api/attack', methods=['POST'])
@app.route('/attack', methods=['POST'])
def attack():
    data = _payload()
    result = engine.attack_target(
        attacker_deity_id=data.get('deity_id', PLAYER_DEITY),
        target_deity_id=data.get('target_deity_id', ''),
        region_id=data.get('region_id', ''),
    )
    return jsonify(result)


@app.route('/api/pray', methods=['POST'])
@app.route('/pray', methods=['POST'])
def pray():
    data = _payload()
    result = engine.pray(
        deity_id=data.get('deity_id', PLAYER_DEITY),
        prayer_type=data.get('prayer_type', 'faith'),
    )
    return jsonify(result)


@app.route('/api/build', methods=['POST'])
@app.route('/build', methods=['POST'])
def build():
    data = _payload()
    result = engine.build_structure(
        deity_id=data.get('deity_id', PLAYER_DEITY),
        building_type=data.get('building_type', ''),
        region_id=data.get('region_id', ''),
    )
    return jsonify(result)


@app.route('/api/miracle', methods=['POST'])
@app.route('/miracle', methods=['POST'])
def miracle():
    data = _payload()
    result = engine.perform_miracle(
        deity_id=data.get('deity_id', PLAYER_DEITY),
        region_id=data.get('region_id', ''),
        miracle_type=data.get('miracle_type', ''),
        intensity=data.get('intensity', 1),
    )
    return jsonify(result)


@app.route('/api/turn', methods=['POST'])
@app.route('/turn', methods=['POST'])
def advance_turn():
    engine.process_turn()
    world = engine.get_world_view()
    world['events'] = engine.state.get_events(limit=10)
    ended = engine.state.turn_info.phase == GamePhase.ENDED
    world['game_over'] = ended
    if ended:
        world['winner'] = engine.state.winner
        world['victory_condition'] = engine.state.victory_condition.value
    return jsonify(world)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
