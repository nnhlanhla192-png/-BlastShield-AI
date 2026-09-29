from flask import Flask, jsonify

app = Flask(__name__)

USERS = {
    1: {"name": "Admin", "role": "admin"},
    2: {"name": "Student", "role": "student"},
}


@app.get("/")
def home():
    return jsonify({"application": "BlastShield Demo", "status": "running"})


@app.delete("/users/<int:user_id>")
def delete_user(user_id):
    current_user = USERS[1]
    if current_user["role"] != "admin":
        return jsonify({"error": "Forbidden"}), 403
    if user_id not in USERS:
        return jsonify({"error": "User not found"}), 404
    return jsonify({"message": f"User {user_id} deleted"}), 200


if __name__ == "__main__":
    app.run(debug=True, port=5000)