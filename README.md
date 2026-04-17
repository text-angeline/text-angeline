# text-angeline

Bible verse SMS service. Text a reference, get the verse back.

## Architecture

- **AWS Lambda** with Function URL (no API Gateway) — handles Telnyx webhook
- **S3** — stores Bible translation XML files
- **Telnyx** — SMS/MMS send/receive

All within AWS Free Tier (1M Lambda requests/month, 5GB S3).

## Deploy

### Prerequisites

- [AWS SAM CLI](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/install-sam-cli.html)
- AWS account with credentials configured
- Telnyx account with messaging profile

### Steps

```bash
# 1. Build and deploy
sam build
sam deploy --guided

# 2. Upload translation XML files to S3
aws s3 sync trans/ s3://BUCKET_NAME/trans/

# 3. Set the webhook URL in Telnyx dashboard
#    Use the WebhookUrl from sam deploy output
```

### Environment Variables

| Variable | Description |
|----------|-------------|
| `TELNYX_KEY` | Telnyx API key |
| `TELNYX_NUMBER` | Telnyx phone number |
| `DEFAULT_TRANS` | Default translation code (default: `niv`) |
| `TRANS_BUCKET` | S3 bucket for XML files |
| `TRANS_PREFIX` | S3 key prefix (default: `trans/`) |

## Usage

Text any Bible reference to **888-766-1494**:

```
John 3:16
Psalm 23
Romans 8:28-30 esv
Genesis 1:1-3, 26-28
```
