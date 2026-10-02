from flask import Flask, jsonify, request

app = Flask(__name__)

USERS = {
    1: {"name": "Admin", "role": "admin"},
    2: {"name": "Student", "role": "student"},
}


def get_current_user():
    """Reads which user is calling from a header. No header = not logged in."""
    user_id = request.headers.get("X-User-Id")
    if user_id is None:
        return None
    return USERS.get(int(user_id))


@app.get("/")
def home():
    return jsonify({"application": "BlastShield Demo", "status": "running"})


@app.delete("/users/<int:user_id>")
def delete_user(user_id):
    current_user = get_current_user()
    if not current_user or current_user["role"] != "admin":
        return jsonify({"error": "Forbidden"}), 403
    if user_id not in USERS:
        return jsonify({"error": "User not found"}), 404
    return jsonify({"message": f"User {user_id} deleted"}), 200


if __name__ == "__main__":
    app.run(debug=True, port=5000)