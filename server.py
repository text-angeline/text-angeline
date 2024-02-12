from flask import Flask, request
import re
import json
import main

app = Flask(__name__)
pattern = r"^((?P<iteration>[1-3] )?(?P<book>[a-zA-Z]{3,})(?: (?P<chapter>\d{1,3}))(?::(?P<verse_1>\d{1,3}))?(?:-(?P<verse_2>\d{1,3}))?(?: (?P<translation>[a-zA-Z]{,4}))?)$"

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

            if (re.match(pattern, user_input)):
                main.init(user_input, user_number)
            else:
                error_message = "Error: Incorrect format!"
                main.send_message(error_message, user_number)
            return '', 200 # Return 200 OK to Telnyx
    except Exception as e:
        print("Error processing webhook:", e)
        return '', 400 # Return 400 Bad Request (catchall)

if __name__ == "__main__":
    app.run(port=8000)
