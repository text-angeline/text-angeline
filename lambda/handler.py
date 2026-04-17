### "What hath God wrought"

import json
import html
from angeline import init, send_message, AngelineError

def receive_sms(event, context):
    try:
        body = json.loads(event.get("body", "{}"))
    except (json.JSONDecodeError, TypeError):
        return {"statusCode": 400, "body": "Bad request"}

    # Telnyx wraps payload in "data" for webhook v2
    data = body.get("data", body)
    event_type = data.get("event_type")

    if (event_type == "message.received"):
        try:
            payload = data.get("payload", {})
            user_input = html.escape(payload["text"])
            user_number = payload["from"]["phone_number"]
            print("user_input:", user_input)
            print("user_number:", user_number)
            init(user_input, user_number)
        except AngelineError as e:
            if e.message:
                msg = f"Error: {e.message}. Please try again." if e.is_error else e.message
                send_message("MMS", msg, user_number)
        except KeyError as e:
            print("Error: Couldn't process webhook; User was not notified.", e)
            return {"statusCode": 400, "body": "Missing field"}

    return {"statusCode": 200, "body": "OK"}
