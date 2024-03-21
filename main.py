import json
import bleach
import angeline

def receive_sms(request, context):
    print(f"Request: {request}")
    # print(f"Context: {context}")
    try:
        event_type = request.get("event_type")
        if (event_type == "message.received"):
            user_input = bleach.clean(request["payload"]["text"])
            user_number = request["payload"]["from"]["phone_number"]
            print("user_input:", user_input)
            print("user_number:", user_number)
            angeline.init(user_input, user_number)
            return "", 200
    except KeyError as e:
        print("Error: Couldn't process webhook; User was not notified.", e)
        return "", 400
