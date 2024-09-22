from flask import Flask, jsonify, request
from models.user import User
from database import db
from flask_login import LoginManager, login_user, current_user, logout_user, login_required

app = Flask(__name__)
app.config['SECRET_KEY'] = "your_secret_key"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'

login_manager = LoginManager()
db.init_app(app)
login_manager.init_app(app)

login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)

@app.route('/login', methods=['POST'])
def login():

    data = request.json
    username = data.get('username')
    password = data.get('password')

    if username and password:

        user = User.query.filter_by(username=username).first()

        if user and user.password == password:
            login_user(user)
            return jsonify({"message": "Credenciais válidas"}), 200

    return jsonify({"message": "Credenciais inválidas"}), 400


@app.route('/logout', methods=['GET'])
@login_required
def logout():
    logout_user()
    return jsonify({"message": "Deslogado com sucesso"}), 200



@app.route('/user/<int:id_user>', methods=['GET'])
@login_required
def read_user(id_user):
    user = User.query.get(id_user)

    if user:
        return {"username": user.username}, 200
    
    return jsonify({"message": "usuario não encontrado"}), 404


@app.route('/user/<int:id_user>', methods=['PUT'])
@login_required
def update_user(id_user):
    data = request.json
    user = User.query.get(id_user)

    if id_user != current_user.id and current_user.role != 'admin':
        return jsonify({"message": "Você não possui permissão para editar outro usuário"}), 403


    if user and data.get('password'):
        user.password = data.get('password')
        db.session.commit()

        return jsonify({"message": f"usuario {id_user} atualizado com sucesso"}), 200
    
    return jsonify({"message": "usuario não encontrado"}), 404


@app.route('/user/<int:id_user>', methods=['DELETE'])
@login_required
def delete_user(id_user):
    user = User.query.get(id_user)

    if current_user.role != 'admin':
        return jsonify({"message": "Você não possui permissão para deletar usuários"}), 403

    if id_user == current_user.id:
        return jsonify({"message": "não é possível deletar o próprio usuário"}), 403

    if user:
        db.session.delete(user)
        db.session.commit()
        return jsonify({"message": f"usuario {id_user} deletado com sucesso"}), 200
    
    return jsonify({"message": "usuario não encontrado"}), 404

@app.route('/user', methods=['POST'])
def create_user():
    data = request.json
    username = data.get('username')
    password = data.get('password')

    if username and password:
        user =  User(username=username, password=password, role='user')
        db.session.add(user)
        db.session.commit()
        return jsonify({"message": "usuario criado com sucesso"}), 201

    return jsonify({"message": "dados invalidos"}), 400

if __name__ == '__main__':
    app.run(debug=True)