### "What hath God wrought"

import json
import html
from angeline import (
    parse_input, fetch_text, build_payload,
    determine_protocol, send_message, AngelineError
)

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
            telnyx_payload = data.get("payload", {})
            user_input = html.escape(telnyx_payload["text"])
            user_number = telnyx_payload["from"]["phone_number"]
            print("user_input:", user_input)
            print("user_number:", user_number)

            ## Parse → Fetch → Build → Send
            request = parse_input(user_input)

            if request["type"] == "command":
                if request["message"]:
                    send_message("MMS", request["message"], user_number)
            else:
                root = fetch_text(request["trans_key"])
                payload = build_payload(root, request)
                protocol = determine_protocol(payload)
                try:
                    send_message(protocol, payload, user_number)
                except Exception:
                    raise AngelineError("Request too large for this translation")

        except AngelineError as e:
            if e.message:
                msg = f"Error: {e.message}. Please try again." if e.is_error else e.message
                send_message("MMS", msg, user_number)
        except KeyError as e:
            print("Error: Couldn't process webhook; User was not notified.", e)
            return {"statusCode": 400, "body": "Missing field"}
        except Exception as e:
            print("Error:", e)
            try:
                send_message("MMS", "Error: Something went wrong. Please try again.", user_number)
            except Exception:
                print("Error: Couldn't send error message; User was not notified.")

    return {"statusCode": 200, "body": "OK"}
