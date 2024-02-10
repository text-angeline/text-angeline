import os
from flask import Flask, request

app = Flask(__name__)

@app.route('/webhooks', methods=['POST'])
def webhooks():
    body = request.json
    print(body)
    return '', 200

if __name__ == "__main__":
    app.run(port=5000)
