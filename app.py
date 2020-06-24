from flask import Flask, jsonify, make_response, request
import json
import hashlib

app = Flask(__name__)


def load_users(path_to_file):
    with open(path_to_file, 'r', encoding='utf-8') as f:
        return json.load(f)


def save_users(path_to_file, data):
    with open(path_to_file, 'w', encoding='utf-8') as f:
        json.dump(data, f)


@app.route('/user/', methods=['GET'])
def get_users():
    return load_users('user.json'), 200


@app.route('/user/<user_id>', methods=['GET'])
def get_user(user_id):
    users = load_users('user.json')

    user = users.get(user_id)
    if user:
        user.pop('password')
        return jsonify(user), 200

    return make_response(jsonify({'error': 'User not found'}), 404)


@app.route('/user/', methods=['POST'])
def create_user():
    users = load_users('user.json')

    if not request.json['login'] or not request.json.get('password'):
        return make_response(jsonify({'error': 'Invalid user data'}), 400)
    elif request.json['login'] in [user['login'] for user in users.values()]:
        return make_response(jsonify({'error': 'User already exist'}), 400)

    password_hash = hashlib.sha224(
        request.json.get('password').encode('utf-8')
    ).hexdigest()
    user = {
        'login': request.json['login'],
        'password': password_hash,
        'name': request.json.get('name', request.json['login']),
    }

    id_ = str(max(int(key) for key in users.keys()) + 1)
    users[id_] = user

    save_users('user.json', users)
    return jsonify({'user_id': id_}), 200


@app.route('/user/<user_id>', methods=['PUT'])
def update_user(user_id):
    users = load_users('user.json')

    if not users.get(user_id):
        return make_response(jsonify({'error': 'User not found'}), 404)
    elif not request.json:
        return make_response(jsonify({'error': 'No new user information'}), 400)
    elif request.json['login'] in [user['login'] for user in users.values()]:
        return make_response(jsonify({'error': 'User already exist'}), 400)

    users[user_id]['login'] = request.json.get('login', users[user_id]['login'])
    if request.json.get('password'):
        users[user_id]['password'] = hashlib.sha224(
            request.json.get('password').encode('utf-8')
        ).hexdigest()
    users[user_id]['name'] = request.json.get('name', users[user_id]['name'])

    save_users('user.json', users)

    users[user_id].pop('password')
    return jsonify(users[user_id]), 201


@app.route('/user/<user_id>', methods=['DELETE'])
def delete_user(user_id):
    users = load_users('user.json')

    if not users.get(user_id):
        return make_response(jsonify({'error': 'User not found'}), 404)
    users.pop(user_id)

    save_users('user.json', users)
    return jsonify({'result': 'User deleted'}), 200


if __name__ == '__main__':
    app.run(debug=True)
