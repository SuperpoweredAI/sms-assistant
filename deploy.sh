set -e

sam build -t resources.yaml --use-container

sam deploy \
    --stack-name sms-assistant-demo-1 \
    --region us-east-1 \
    --no-confirm-changeset \
    --resolve-s3 \
    --capabilities CAPABILITY_IAM \
    --parameter-overrides ParameterKey=Environment,ParameterValue=dev