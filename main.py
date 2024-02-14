from flask import Flask, request
import re
import json
import main
# Comment out for local:
import functions_framework

app = Flask(__name__)

# Comment out for local:
@functions_framework.cloud_event
@app.route('/webhooks', methods=['POST'])
def webhooks():
    try:
        telnyx_response = request.json
        event_type = telnyx_response.get('data', {}).get('event_type') 
        if event_type == "message.received":
            user_input = telnyx_response['data']['payload']['text']
            user_number = telnyx_response['data']['payload']['from']['phone_number']
            print("NEW REQUEST")
            print(telnyx_response, end="\n")
            print("user_input:", user_input)
            print("user_number:", user_number)
            main.init(user_input, user_number)
            return '', 200 # Return 200 OK to Telnyx
    except Exception as e:
        print("Error processing webhook:", e)
        return '', 400 # Return 400 Bad Request (catchall)

if __name__ == "__main__":
    app.run(port=8000)
