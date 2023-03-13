set -e

sam build -t resources.yaml --use-container

sam deploy \
    --stack-name sms-demo \
    --region us-east-1 \
    --no-confirm-changeset \
    --resolve-s3 \
    --capabilities CAPABILITY_IAM \
    --parameter-overrides \
        ParameterKey=Environment,ParameterValue=dev \
        ParameterKey=SuperpoweredModelId,ParameterValue=c8a058d3-84a2-4a4a-af98-75259c42e52e \
        ParameterKey=TwilioPhoneNumber,ParameterValue=+18446037222
