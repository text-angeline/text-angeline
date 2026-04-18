### "What hath God wrought"

import json
import boto3
from angeline import (
    parse_input, fetch_text, build_payload,
    determine_protocol, send_message, send_error,
    AngelineError
)

lambda_client = boto3.client('lambda')

def receive_sms(event, context):
    ## Webhook entry — immediately delegate to async self-invoke and return 200
    if "requestContext" in event:
        lambda_client.invoke(
            FunctionName=context.function_name,
            InvocationType='Event',
            Payload=json.dumps({"task_body": event.get("body", "{}")})
        )
        return {"statusCode": 200}

    ## Async invocation — do the actual work
    body_str = event.get("task_body")
    if not body_str:
        return {"statusCode": 200}

    user_number = None

    try:
        body = json.loads(body_str)
        data = body.get("data", body)

        if data.get("event_type") != "message.received":
            return {"statusCode": 200}

        p = data.get("payload", {})
        user_input = p["text"]
        user_number = p["from"]["phone_number"]

        req = parse_input(user_input)
        root = fetch_text(req["trans_key"])
        text_out = build_payload(root, req)
        determine_protocol(text_out)
        send_message(text_out, user_number)

    except AngelineError as e:
        if user_number:
            try:
                send_error(str(e), user_number)
            except Exception:
                print(f"Failed to send error reply: {e}")
        else:
            print(f"AngelineError (no user to reply to): {e}")
    except Exception as e:
        print(f"Error: {e}")

    return {"statusCode": 200}

