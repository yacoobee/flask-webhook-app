from flask import Flask, request, jsonify, render_template
import socket

app = Flask(__name__)

# Store received webhooks in-memory
webhook_store = []

@app.route('/')
def index():
    return render_template('index.html', webhooks=webhook_store)

@app.route('/webhook', methods=['POST'])
def webhook():
    if request.is_json:
        data = request.get_json()
        webhook_store.append(data)  # Store the webhook data
        print("Received JSON data:", data)
        return jsonify({"message": "Webhook has been received!", "data": data}), 200
    else:
        return jsonify({"error": "Invalid request format, expected JSON"}), 400

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
