from flask import Flask, request
import main
import json

app = Flask(__name__)

@app.route('/webhooks', methods=['POST'])
def webhooks():
    try:
        telnyxData = request.json
        event_type = telnyxData.get('data', {}).get('event_type')
        
        if event_type == "message.received":
            sms = telnyxData['data']['payload']['text']
            sender = telnyxData['data']['payload']['from']['phone_number']
            
            print(telnyxData)
            print()
            print("Received SMS:", sms)
            print("From:", sender)
            
            main.send(sms, sender)
            
            return '', 200  # Return 200 OK to Telnyx
        
    except Exception as e:
        print("Error processing webhook:", e)
        return '', 400  # Return 400 Bad Request for any errors

if __name__ == "__main__":
    app.run(port=8000)
