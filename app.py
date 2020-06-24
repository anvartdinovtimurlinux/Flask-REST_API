from flask import Flask, jsonify, abort, make_response, request
import json
import hashlib

app = Flask(__name__)


@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)


@app.route('/user/', methods=['GET'])
def get_users():
    with open('user.json', 'r', encoding='utf-8') as f:
        return jsonify({'users': json.load(f)})


@app.route('/user/<user_id>', methods=['GET'])
def get_user(user_id):
    with open('user.json', 'r', encoding='utf-8') as f:
        users = json.load(f)

    user = users.get(user_id)
    if user:
        user['user_id'] = user_id
        return jsonify({'user': user})
    abort(404)


@app.route('/user/', methods=['POST'])
def create_user():
    with open('user.json', 'r', encoding='utf-8') as f:
        users = json.load(f)

    password_hash = hashlib.sha224(
        request.json.get('password').encode('utf-8')
    ).hexdigest()
    user = {
        'login': request.json['login'],
        'password': password_hash,
        'name': request.json.get('name'),
    }

    id_ = str(max(int(key) for key in users.keys()) + 1)
    users[id_] = user

    with open('user.json', 'w', encoding='utf-8') as f:
        json.dump(users, f)
    return jsonify({id_: user}), 201


@app.route('/user/<user_id>', methods=['PUT'])
def update_user(user_id):
    with open('user.json', 'r', encoding='utf-8') as f:
        users = json.load(f)

    if not users.get(user_id):
        abort(404)
    if not request.json:
        abort(400)

    users[user_id]['login'] = request.json.get('login', users[user_id]['login'])
    if request.json.get('password'):
        users[user_id]['password'] = hashlib.sha224(
            request.json.get('password').encode('utf-8')
        ).hexdigest()
    users[user_id]['name'] = request.json.get('name', users[user_id]['name'])

    with open('user.json', 'w', encoding='utf-8') as f:
        json.dump(users, f)
    return jsonify({'user': users[user_id]})


@app.route('/user/<user_id>', methods=['DELETE'])
def delete_user(user_id):
    with open('user.json', 'r', encoding='utf-8') as f:
        users = json.load(f)

    if not users.get(user_id):
        abort(404)
    users.remove(users(user_id))

    with open('user.json', 'w', encoding='utf-8') as f:
        json.dump(users, f)
    return jsonify({'result': True})


if __name__ == '__main__':
    app.run(debug=True)
