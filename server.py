from flask import Flask, request
import json
import main

app = Flask(__name__)

@app.route('/webhooks', methods=['POST'])
def webhooks():
    try:
        t_response = request.json
        event_type = t_response.get('data', {}).get('event_type') 
        if event_type == "message.received":
            sms = t_response['data']['payload']['text']
            sender = t_response['data']['payload']['from']['phone_number']
            
            print(t_response, end="\n")
            print("Received SMS:", sms)
            print("From:", sender)
            
            main.send(user_input, user_number)
            return '', 200 # Return 200 OK to Telnyx
    except Exception as e:
        print("Error processing webhook:", e)
        return '', 400 # Return 400 Bad Request for any errors

if __name__ == "__main__":
    app.run(port=8000)
