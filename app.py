from flask import Flask, jsonify, request
import json
import hashlib

app = Flask(__name__)


def load_users(path_to_file):
    with open(path_to_file, 'r', encoding='utf-8') as f:
        try:
            data = json.load(f)
        except ValueError:
            data = {}
        return data


def save_users(path_to_file, data):
    with open(path_to_file, 'w', encoding='utf-8') as f:
        json.dump(data, f)


def create_user_dict(name, login, password=None):
    user = {
        'login': login,
        'name': name,
    }
    if password:
        user['password'] = hashlib.sha224(password.encode('utf-8')).hexdigest()

    return user


@app.route('/user/', methods=['GET'])
def get_users():
    users = load_users('user.json')
    users_without_password = [{
        'login': user['login'],
        'name': user['name']
    } for user in users.values()]
    return jsonify(users_without_password), 200


@app.route('/user/<user_id>', methods=['GET'])
def get_user(user_id):
    users = load_users('user.json')

    user = users.get(user_id)
    if user:
        user.pop('password')
        return jsonify(user), 200

    return jsonify({'error': 'User not found'}), 404


@app.route('/user/', methods=['POST'])
def create_user():
    users = load_users('user.json')

    if not request.json.get('login') or not request.json.get('password'):
        return jsonify({'error': 'Invalid user data'}), 400
    elif request.json.get('login') in [user['login'] for user in users.values()]:
        return jsonify({'error': 'User already exist'}), 400

    user = create_user_dict(
        request.json.get('name', request.json.get('login')),
        request.json.get('login'),
        request.json.get('password')
    )
    if len(users):
        user_id = str(max(int(key) for key in users.keys()) + 1)
    else:
        user_id = 0
    users[user_id] = user

    save_users('user.json', users)
    return jsonify({'user_id': user_id}), 201


@app.route('/user/<user_id>', methods=['PUT'])
def update_user(user_id):
    users = load_users('user.json')

    if not users.get(user_id):
        return jsonify({'error': 'User not found'}), 404
    elif not request.json:
        return jsonify({'error': 'No new user information'}), 400
    elif request.json.get('login') in [user['login'] for user in users.values()]:
        return jsonify({'error': 'This login already exists'}), 400

    user = create_user_dict(
        request.json.get('name', users[user_id]['name']),
        request.json.get('login', users[user_id]['login']),
        request.json.get('password')
    )
    users[user_id].update(user)
    save_users('user.json', users)

    if user.get('password'):
        user.pop('password')
    return jsonify(user), 200


@app.route('/user/<user_id>', methods=['DELETE'])
def delete_user(user_id):
    users = load_users('user.json')

    if not users.get(user_id):
        return jsonify({'error': 'User not found'}), 404
    users.pop(user_id)

    save_users('user.json', users)
    return jsonify({'result': 'User deleted'}), 200


if __name__ == '__main__':
    app.run(debug=True)
