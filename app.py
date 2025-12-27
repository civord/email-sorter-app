from flask import Flask, render_template, jsonify, request
import database

app = Flask(__name__)

@app.route("/")
def index():
    emails = database.get_raw_email_table()
    return render_template("index.html", emails=emails)

@app.route("/email/<int:email_id>")
def get_email(email_id):
    email = database.get_email(email_id)
    if not email:
        return jsonify({"error": "Not Found"}), 404
    
    return jsonify({
        "sender": email["sender"],
        "subject": email["subject"],
        "body": email["body"],
        "date": email["date"]
    })

@app.route("/api/submit-data", methods=['POST'])
def get_email_status():
    if request.method == "POST":
        data = request.get_json()
        email_id = data.get("email_id")
        email_status = data.get("email_status")
        if not email_id or not email_status:
            return jsonify({"error": "Invalid payload"}), 400
        
        database.update_email_status(email_id, email_status)

        return jsonify({"success": True})

if __name__ == "__main__":
    app.run(debug=True)