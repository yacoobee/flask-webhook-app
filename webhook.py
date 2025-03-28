from flask import Flask, request, jsonify, render_template, send_file, Response
import json
import os
import time

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

@app.route('/stream')
def stream():
    def event_stream():
        last_index = 0

        # Send all existing webhooks first
        for webhook in webhook_store:
            yield f"data: {json.dumps(webhook)}\n\n"
            last_index += 1

        # Then, wait for new webhooks in real-time
        while True:
            if last_index < len(webhook_store):
                new_data = webhook_store[last_index]
                yield f"data: {json.dumps(new_data)}\n\n"
                last_index += 1
            time.sleep(1)
    
    return Response(event_stream(), content_type='text/event-stream')


@app.route('/clear', methods=['POST'])
def clear_webhooks():
    webhook_store.clear()
    return jsonify({"message": "Webhook cache cleared"}), 200

@app.route('/save', methods=['GET'])
def save_webhooks():
    filename = "webhooks.txt"
    with open(filename, "w") as file:
        json.dump(webhook_store, file, indent=4)
    return send_file(filename, as_attachment=True)

@app.route('/delete', methods=['POST'])
def delete_webhooks():
    webhook_store.clear()
    if os.path.exists("webhooks.txt"):
        os.remove("webhooks.txt")
    return jsonify({"message": "All webhook records deleted"}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
