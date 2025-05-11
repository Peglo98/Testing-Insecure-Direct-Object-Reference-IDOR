# Flask IDOR Lab

This repository contains two Flask-based REST API implementations demonstrating the concept of Insecure Direct Object Reference (IDOR) and how to properly secure against it.

## Repository Structure
```
lab1_idor/
├── vulnerable/      # API with IDOR vulnerability
│   ├── app.py
│   ├── auth.py
│   ├── models.py
│   ├── requirements.txt
└── patched/          # API with IDOR fixed
    ├── app.py
    ├── auth.py
    ├── models.py
    ├── requirements.txt
```

## Overview
1. Build a Flask REST API supporting CRUD operations on `Product` resources belonging to authenticated users.
2. Use simple auto-incrementing integer IDs for products.
3. Demonstrate how an attacker can exploit IDOR to access another user’s products by guessing or enumerating IDs.
4. Test the vulnerability using Burp Suite (Proxy, Repeater, Intruder).
5. Apply a fix by enforcing owner-based filtering on all product endpoints.

## Getting Started

Both subfolders (`vulnerable` and `patched`) follow the same setup steps.

### Prerequisites
- Python 3.10+
- `pip` and virtual environment support

### Installation
```bash
# Navigate into the chosen folder
cd vulnerable   # or 'patched'

# Create and activate a virtual environment
python -m venv .venv
source .venv/bin/activate   # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Running the Server
```bash
export FLASK_APP=app.py
export FLASK_ENV=development   # enables debug mode
flask run
```
Server will listen by default on `http://127.0.0.1:5000`.

## API Endpoints

### Authentication
- `POST /register` – Register a new user.  
  Request JSON: `{ "username": "alice", "password": "pass123" }`
- `POST /login` – Obtain JWT token.  
  Request JSON: `{ "username": "alice", "password": "pass123" }`  
  Response JSON: `{ "token": "<JWT_TOKEN>" }`

### Products
- `POST /products` – Create a new product.  
  Headers: `Authorization: Bearer <JWT_TOKEN>`  
  Request JSON: `{ "name": "My Product" }`
- `GET /products/<id>` – Get a product by ID. Requires valid JWT.
- `PUT /products/<id>` – Update a product. Requires valid JWT.  
  Request JSON: `{ "name": "Updated Name" }`
- `DELETE /products/<id>` – Delete a product. Requires valid JWT.

> In the **vulnerable** version, `GET /products/<id>` does not verify ownership and will return any product if you guess the ID.  
> In the **secure** version, all endpoints filter by the authenticated user’s `owner_id`, preventing IDOR.

## Testing IDOR with Burp Suite
1. Configure your browser or Postman to use Burp’s proxy (`127.0.0.1:8080`).  
2. Turn on **Intercept** in Burp.  
3. Log in as User A and create products (IDs 1..n).  
4. Log in as User B and send `GET /products/1`. Observe that the **vulnerable** server returns User A’s product.  
5. Use **Repeater** or **Intruder** to enumerate IDs automatically.

## Fixing IDOR
The secure implementation applies owner-based filtering on all product operations:
```python
Product.query.filter_by(id=product_id, owner_id=g.current_user.id).first_or_404()
```
This change ensures a user can only access their own products.
