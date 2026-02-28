from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import (
    JWTManager,
    jwt_required,
    get_jwt_identity
)
from config import Config
from flask_migrate import Migrate


app = Flask(__name__)
app.config.from_object(Config)

db = SQLAlchemy(app)
jwt = JWTManager(app)

migrate = Migrate(app, db)

# -------------------------
# Product Model
# -------------------------
class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    price = db.Column(db.Float, nullable=False)
    owner = db.Column(db.String(100), nullable=False)  # username from JWT


# -------------------------
# Add Product
# -------------------------
@app.route("/products", methods=["POST"])
@jwt_required()
def add_product():
    current_user = get_jwt_identity()
    data = request.get_json()

    product = Product(
        name=data["name"],
        price=data["price"],
        owner=current_user
    )

    db.session.add(product)
    db.session.commit()

    return jsonify({"message": "Product added"}), 201


# -------------------------
# Get All Products
# -------------------------
@app.route("/products", methods=["GET"])
@jwt_required()
def get_products():
    current_user = get_jwt_identity()

    products = Product.query.filter_by(owner=current_user).all()

    output = []
    for product in products:
        output.append({
            "id": product.id,
            "name": product.name,
            "price": product.price
        })

    return jsonify(output), 200


# -------------------------
# Delete Product
# -------------------------
@app.route("/products/<int:id>", methods=["DELETE"])
@jwt_required()
def delete_product(id):
    current_user = get_jwt_identity()

    product = Product.query.filter_by(id=id, owner=current_user).first()

    if not product:
        return jsonify({"message": "Product not found"}), 404

    db.session.delete(product)
    db.session.commit()

    return jsonify({"message": "Product deleted"}), 200


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)