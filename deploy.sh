#!/usr/bin/env bash
### "What hath God wrought"
set -euo pipefail

FUNCTION="angeline-AngelineFunction-frs1NjziBwiW"
BUCKET="angeline-translations-973932300890"
ZIP="deployment_package.zip"

usage() {
    echo "Usage: ./deploy.sh [code|trans|all]"
    echo "  code  - Deploy Lambda code only"
    echo "  trans - Sync translations to S3 only"
    echo "  all   - Deploy code + sync translations"
    exit 1
}

deploy_code() {
    echo "==> Updating Lambda code..."
    cp lambda/handler.py lambda/angeline.py .
    zip "$ZIP" handler.py angeline.py
    rm handler.py angeline.py
    aws lambda update-function-code \
        --function-name "$FUNCTION" \
        --zip-file "fileb://$ZIP" \
        --query 'CodeSha256' --output text
    echo "==> Code deployed."
}

deploy_trans() {
    echo "==> Syncing translations to S3..."
    aws s3 sync trans/ "s3://$BUCKET/trans/" --size-only
    echo "==> Translations synced."
}

case "${1:-}" in
    code)  deploy_code ;;
    trans) deploy_trans ;;
    all)   deploy_code; deploy_trans ;;
    *)     usage ;;
esac
