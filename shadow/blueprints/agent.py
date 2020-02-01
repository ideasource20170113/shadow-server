from flask import Blueprint, render_template, abort, current_app, send_from_directory
from shadow.models import Agent
from flask_login import current_user

agent_bp = Blueprint('agent', __name__, url_prefix='/agent')
online_users = []


@agent_bp.route('/')
def home():
    uid = current_user.email
    agents = Agent.query.filter_by(user_email=uid).all()
    return render_template('agent/home.html', agents=agents)


@agent_bp.route('/shell/<agent_id>/')
def agent_console(agent_id):
    agent = Agent.query.get(agent_id)
    if not agent:
        abort(404)
    return render_template('agent/_agent_console.html', agent=agent)


@agent_bp.route('/uploads/<path:path>')
def uploads(path):
    print(send_from_directory(current_app.config['UPLOAD_FOLDER'], path))
    return send_from_directory(current_app.config['UPLOAD_FOLDER'], path)
