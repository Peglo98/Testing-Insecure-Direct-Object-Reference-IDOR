from flask import Flask, request, jsonify, abort, g
from flask_sqlalchemy import SQLAlchemy
from models import db, User, Product
from auth import authenticate, jwt_required, hash_password

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///lab1.db'
app.config['SECRET_KEY'] = '7612b4c291d7eba71a2e368bf115cfb2dbe71bb6684bb997a4954c446f3ab42350cde37945ac4fb232091118274c39f840a3220ad98774e9fc8d1cb759ed8b24da9d711532c526e19e7e87d9146e77005317b1766e82749ae2d6561bbe3f65817185ed9c50c9e09ef1aa9964cdbe86e548693608299fd4025e3a011a7d3c744e735545e7c689840ce90b6d0df5f7d50842e9e471ab6ca353b07f8d24aaf2ffd6fad9f581634e5c69df84b4cd09922e65ec5e877b35f781b776994b60270b3cc4127f4a01121e8f192fceea9f9db6b9ff61fc4918ffd04daf43a4245311e405ffdf1c0aca3aa8cdd57bde72bcf27211d3c1579ef2cc1ecadf19ed0418c2125ef2'
db.init_app(app)

@app.before_first_request
def init_db():
    db.create_all()

# Rejestracja użytkownika
def register_user(username, password):
    if User.query.filter_by(username=username).first():
        abort(400, 'Użytkownik już istnieje')
    user = User(username=username, password_hash=hash_password(password))
    db.session.add(user)
    db.session.commit()

@app.route('/register', methods=['POST'])
def register():
    data = request.get_json(force=True)
    if 'username' not in data or 'password' not in data:
        abort(400, description="Proszę podać 'username' i 'password'.")
    register_user(data['username'], data['password'])
    return '', 201

# Logowanie – zwracamy JWT
@app.route('/login', methods=['POST'])
def login():
    data = request.get_json(force=True)
    if 'username' not in data or 'password' not in data:
        abort(400, description="Proszę podać 'username' i 'password'.")
    token = authenticate(data['username'], data['password'])
    if not token:
        abort(401)
    return jsonify(token=token)

# CREATE
@app.route('/products', methods=['POST'])
@jwt_required
def create_product():
    data = request.get_json(force=True)
    if not data or 'name' not in data:
        abort(400, description="Proszę podać pole 'name'.")
    p = Product(name=data['name'], owner_id=g.current_user.id)
    db.session.add(p)
    db.session.commit()
    return jsonify(id=p.id, name=p.name), 201

# READ (IDOR demonstration)
@app.route('/products/<int:product_id>', methods=['GET'])
@jwt_required
def get_product(product_id):
    p = Product.query.get_or_404(product_id)
    return jsonify(id=p.id, name=p.name, owner=p.owner.username)

# UPDATE
@app.route('/products/<int:product_id>', methods=['PUT'])
@jwt_required
def update_product(product_id):
    p = Product.query.get_or_404(product_id)
    if p.owner_id != g.current_user.id:
        abort(403)
    data = request.get_json(force=True)
    if not data or 'name' not in data:
        abort(400, description="Proszę podać pole 'name'.")
    p.name = data['name']
    db.session.commit()
    return jsonify(id=p.id, name=p.name)

# DELETE
@app.route('/products/<int:product_id>', methods=['DELETE'])
@jwt_required
def delete_product(product_id):
    p = Product.query.get_or_404(product_id)
    if p.owner_id != g.current_user.id:
        abort(403)
    db.session.delete(p)
    db.session.commit()
    return '', 204

if __name__ == '__main__':
    app.run(debug=True)