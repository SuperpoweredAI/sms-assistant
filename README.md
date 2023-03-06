# Superpowered AI SMS Assistant Demo

In this demo, we will build a production-ready SMS Assistant with the Superpowered.ai API.

### High-level overview

Set up Twilio account so you have can access their services via API. This will allow us to receive and respond to text messages from a specific number.

Set up AWS account because that's where we'll host our service. We are deploying via AWS SAM (Serverless Application Model). This way, you only pay for what you use and AWS has a generous free tier.

_NOTE: We're using AWS SAM here because of the general ease to get things deployed into production quickly and reliably. You could certainly set up a server in some other way to receive webhooks and respond to SMS messages._

Create your Superpowered model spec that will be used for responding to messages sent to your Twilio phone number. Feel free to get creative here!

The following resources will be created from `resources.yaml`

- An API Gateway that will be how we can receive webhooks when new messages are sent to you Twilio phone number.
- A simple key/value database table that maps phone numbers to model instances. This will ensure that each phone number is associated with its own chat history.
- A Lambda function (triggered by a webhook sent to an API Gateway endpoint) that will take the incoming message and use the Superpowered.ai API `/models/{model_id}/instances/{instance_id}/get_response` endpoint to get an AI response to the message a user sent to your Twilio number.

Things you'll need to do before you can deploy your AI SMS Assistant:

1. Setup your Twilio account and register a phone number:
    - https://www.twilio.com/try-twilio
    - Get your "Account SID" and "Auth Token" from the Twilio Console: https://twilio.com/console
    - Create a phone number via the console or via the CLI: https://www.twilio.com/blog/register-phone-number-send-sms-twilio-cli
2. Create an AWS account and download the SAM CLI:
    - https://aws.amazon.com/free/
    - https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/install-sam-cli.html
3. Create your Superpowered.ai account and API keys:
    - https://superpowered.ai/
    - Login and click "Account" on the left navigation and then click "Create new API key"
4. Save credentials to AWS Systems Manager > Parameter Store as `SecureString` parameters. This is to ensure safety of your API keys.
