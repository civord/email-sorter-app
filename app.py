from flask import Flask, render_template, jsonify, request
import database
from datetime import datetime

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/emails")
def render_emails():
    offset = int(request.args.get("offset", 0))
    limit = int(request.args.get("limit", 20))
    category = request.args.get("category")
    priority = request.args.get("priority")
    emails = database.fetch_emails_batch(offset, limit, category, priority)
    if not emails:
        return jsonify([])

    return jsonify(emails)

@app.route("/email/<int:email_id>")
def get_email(email_id):
    email = database.get_email(email_id)
    if not email:
        return jsonify({"error": "Not Found"}), 404
    
    date = datetime.strptime(email["date"], "%a, %d %b %Y %H:%M:%S %z").strftime("%d/%m/%Y, %H:%M")

    return jsonify({
        "sender": email["sender"],
        "subject": email["subject"],
        "body": email["body"],
        "date": date
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