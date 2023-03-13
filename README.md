# Superpowered AI SMS Assistant Demo

_Superpowered AI is in a free research beta phase. Please join our Discord server for asking questions, giving feedback, talking about ideas, or just to say hey!: https://discord.gg/PD6qE85kch_

**Superpowered AI makes it easy to add superpowers like memory :zap:, knowledge :book:, and tools :wrench: to augment LLMs and drastically improve their capabilities.**

**In this demo, we will build an AI assistant with a dedicated phone number (issued via Twilio).**

**Users simply text the AI's number and an individual chat thread (a Superpowered "[Model Instance](!https://www.notion.so/superpoweredai/Superpowered-AI-Documentation-d49b1919720a499188b141b9225d903d?pvs=4#72d39bfca340490e808e5c8ead65f5a8)") will be created and tied to the end-user's phone number. No need to maintain chat histories on your own. That is taken care of by Superpowered.**

Feel free to text 844-603-7222 to interact with an AI assistant we've created from the steps outlined below.

**Tech stack is AWS Serverless. No need to keep a server up and running to respond to Twilio webhooks.**

To get more familiar with the key concepts behind Superpowered, please visit our docs: https://superpoweredai.notion.site/

Take a look at our [API Reference](!https://superpowered.ai/docs)

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
    - https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html
    - https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/install-sam-cli.html
3. Create your Superpowered.ai account and API keys:
    - https://superpowered.ai/
    - Login and click "Account" on the left navigation and then click "Create new API key"
    - Run `aws configure` on the command line to configure AWS credentials and default region.
4. Save credentials to AWS Systems Manager > Parameter Store as `SecureString` parameters. This is to ensure safety of your API keys.

Create 4 SSM Parameters corresponding to the following (they can be anything you want, but will need to be referenced in step #6): `TwilioAccountSid`, `TwilioAuthToken`, `SpApiKeyId`, `SpApiKeySecret`

```bash
aws ssm put-parameter \
    --name  "parameter-name" \
    --value "parameter-value" \
    --type SecureString
```

**NOTE:** The names of these SSM parameters can change as long as the 

5. Create a Superpowered model via the [Dashboard](!https://superpowered.ai/dashboard/models) or via the [API](!https://superpowered.ai/docs) and obtain the Superpowered `model_id`. See `create_model_rest.py` for an example of how to create a model via our REST API.
ß
6. Deploy your SMS Assistant:

Build:
```bash
# sam build may take a while on the first build but should be faster on subsequent runs
# if you're running this from Linux, you may be able to remove the --use-container flag.
sam build -t resources.yaml --use-container
```

Deploy:
```
sam deploy \
    --stack-name sms-demo \
    --no-confirm-changeset \
    --resolve-s3 \
    --capabilities CAPABILITY_IAM \
    --parameter-overrides \
        ParameterKey=Environment,ParameterValue=dev \
        ParameterKey=SuperpoweredModelId,ParameterValue=<MODEL_ID> \
        ParameterKey=TwilioPhoneNumber,ParameterValue=+1XXXXXXXXXX \
        ParameterKey=TwilioAccountSidParamName ParameterValue=twilio-account-sid \
        ParameterKey=TwilioAuthTokenParamName,ParameterValue=twilio-auth-token \
        ParameterKey=SpApiKeyIdParamName,ParameterValue=sp-sms-demo-api-key-id \
        ParameterKey=SpApiKeySecretParamName,ParameterValue=sp-sms-demo-api-key-secret \
        ParameterKey=AiName,ParameterValue=Alfred
```

### Extending The SMS AI Assistant

Here are some ideas for how you can use this demo to create a full-fledge product or business:

##### Multi-Channel Conversations

Instead of just mapping a phone number to a Superpowered [Model Instance](!https://www.notion.so/superpoweredai/Superpowered-AI-Documentation-d49b1919720a499188b141b9225d903d?pvs=4#72d39bfca340490e808e5c8ead65f5a8), you can have any number of identifiers for users. For example, if you map email, phone, Discord username, etc. to the same model instance, the AI agent will maintain a single conversational thread across multiple channels.


##### Customer Support

Add [knowledge bases](!https://superpoweredai.notion.site/d49b1919720a499188b141b9225d903d#521c0632c4694a86a525be9670750c83) to your Superpowered model with information specific to your organization. Your AI assistant will be able to text existing and potential customers.
