#!/usr/bin/env bash
### "What hath God wrought"
set -euo pipefail

STACK="${ANGELINE_STACK:-angeline}"
ZIP="deployment_package.zip"

FUNCTION=$(aws cloudformation describe-stack-resources \
    --stack-name "$STACK" --logical-resource-id AngelineFunction \
    --query 'StackResources[0].PhysicalResourceId' --output text)

BUCKET=$(aws cloudformation describe-stacks \
    --stack-name "$STACK" \
    --query "Stacks[0].Outputs[?OutputKey=='TranslationsBucket'].OutputValue" \
    --output text)

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
