# SMS Assistant

Project outline:
1. Create Twilio account / API keys
    - Need auth token, sid, and phone number
2. Set up serverless API to receive SMS webhooks (so a lambda function can be triggered that responds)
    - Create resources YAML file
    - A DB to map phone numbers to `instance_id`s
    - Create lambda handler function to 1) Parse incoming message, 2) Make Superpowered API call to get_response endpoint, and 3) Send response message
    - Have AWS SAM configured: https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html
3. Create Superpowered model
4. Deploy cloud environment
5. Configure URL to receive the webhooks for incoming messages
