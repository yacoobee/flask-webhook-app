from flask import Flask, request, jsonify, render_template, send_file, Response
import json
import sqlite3
import os
import time

app = Flask(__name__)

# Database file
DB_FILE = "webhooks.db"

# Initialize Database
def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS webhooks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT, 
                    data TEXT)''')
    conn.commit()
    conn.close()

init_db()

@app.route('/')
def index():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT data FROM webhooks")
    webhooks = [json.loads(row[0]) for row in c.fetchall()]
    conn.close()

    return render_template('index.html', webhooks=webhooks)

@app.route('/webhook', methods=['POST'])
def webhook():
    if request.is_json:
        data = request.get_json()

        # Store in SQLite
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute("INSERT INTO webhooks (data) VALUES (?)", (json.dumps(data),))
        conn.commit()
        conn.close()

        print("Received JSON data:", data)
        return jsonify({"message": "Webhook received", "data": data}), 200
    else:
        return jsonify({"error": "Invalid request format, expected JSON"}), 400

@app.route('/stream')
def stream():
    def event_stream():
        last_id = 0
        while True:
            conn = sqlite3.connect(DB_FILE)
            c = conn.cursor()
            c.execute("SELECT id, data FROM webhooks WHERE id > ?", (last_id,))
            rows = c.fetchall()
            conn.close()

            for row in rows:
                last_id = row[0]
                yield f"data: {row[1]}\n\n"

            time.sleep(1)

    return Response(event_stream(), content_type='text/event-stream')

@app.route('/clear', methods=['POST'])
def clear_webhooks():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("DELETE FROM webhooks")
    conn.commit()
    conn.close()
    return jsonify({"message": "Webhook cache cleared"}), 200

@app.route('/save', methods=['POST'])
def save_webhooks():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT data FROM webhooks")
    webhooks = [json.loads(row[0]) for row in c.fetchall()]
    conn.close()

    filename = "webhooks.txt"
    with open(filename, "w") as file:
        json.dump(webhooks, file, indent=4)

    return send_file(filename, as_attachment=True)

@app.route('/delete', methods=['POST'])
def delete_webhooks():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("DELETE FROM webhooks")
    conn.commit()
    conn.close()

    if os.path.exists("webhooks.txt"):
        os.remove("webhooks.txt")

    return jsonify({"message": "All webhook records deleted"}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
