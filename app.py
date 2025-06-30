from flask import Flask, render_template
import database

app = Flask(__name__)

@app.route("/")
def index():
    emails = database.get_raw_email_table()
    return render_template("index.html", emails=emails)

if __name__ == "__main__":
    app.run(debug=True)