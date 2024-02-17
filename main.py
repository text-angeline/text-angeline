import json
import angeline

def telnyx_sms_receiver(request, context):
    # Parse the request body
    print(f"Request: {request}\nContext: {context}")
    try:
        event_type = request.get('event_type')
        if (event_type == 'message.received'):
            user_input = request['payload']['text']
            user_number = request['payload']['from']['phone_number']
            print("user_input:", user_input)
            print("user_number:", user_number)
            angeline.init(user_input, user_number)
            return '', 200  # Return 200 OK to Telnyx
    except Exception as e:
        print("Error processing webhook:", e)
        return '', 400  # Return 400 Bad Request (catchall)
