# twilio documentation about webhooks: https://www.twilio.com/docs/messaging/guides/webhook-request
import base64
import boto3
import json
import os
import urllib
import urllib3  # lambda doesn't have the requests module by default, so we'll just use urllib3
from urllib.parse import parse_qs

from twilio.rest import Client
from twilio.request_validator import RequestValidator


HTTP = urllib3.PoolManager()
SP_MODEL_ID = os.environ['SP_MODEL_ID']

dynamodb = boto3.resource('dynamodb')
ddb_table = dynamodb.Table(os.environ.get('PHONE_NUMBER_TO_INSTANCE_ID_MAP_TABLE_NAME'))


# GET CREDENTIALS FROM SSM
# THIS STEP ASSUMES THAT YOU HAVE STORED YOUR CREDENTIALS IN SSM
# twilio
ssm = boto3.client('ssm')
TWILIO_ACCOUNT_SID = ssm.get_parameter(
    Name=os.environ['TWILIO_ACCOUNT_SID_PARAM_NAME'],
    WithDecryption=True
)['Parameter']['Value']
TWILIO_AUTH_TOKEN = ssm.get_parameter(
    Name=os.environ['TWILIO_AUTH_TOKEN_PARAM_NAME'],
    WithDecryption=True
)['Parameter']['Value']
TWILIO_CLIENT = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

# superpowered
SP_API_KEY_ID = ssm.get_parameter(
    Name=os.environ['SP_API_KEY_ID_PARAM_NAME'],
    WithDecryption=True
)['Parameter']['Value']
SP_API_KEY_SECRET = ssm.get_parameter(
    Name=os.environ['SP_API_KEY_SECRET_PARAM_NAME'],
    WithDecryption=True
)['Parameter']['Value']

encoded_token = base64.b64encode(bytes(f'{SP_API_KEY_ID}:{SP_API_KEY_SECRET}', 'utf-8')).decode('utf-8')
HEADERS = {'Authorization': f'Bearer {encoded_token}'}
BASE_URL = 'https://api.superpowered-qa.com/v1'


def create_superpowered_model_instance(phone_number: str) -> str:
    # create the model instance
    resp = HTTP.request(
        'POST',
        f'{BASE_URL}/models/{SP_MODEL_ID}/instances',
        headers=HEADERS,
        body=json.dumps({'supp_id': phone_number})
    )
    if not resp.status == 200:
        raise Exception(f'Error creating model instance: {resp.data}')

    # get the instance id from the response
    return json.loads(resp.data)['id']


def get_response_from_superpowered_model(instance_id: str, input: dict) -> str:
    # get the response from the model
    resp = HTTP.request(
        'POST',
        f'{BASE_URL}/models/{SP_MODEL_ID}/instances/{instance_id}/get_response',
        headers=HEADERS,
        body=json.dumps({'input': input})
    )
    if not resp.status == 200:
        raise Exception(f'Error getting response from model: {resp.data}')

    # get the response from the response
    return json.loads(resp.data)['model_response']['content']


def send_twilio_response(to: str, from_: str, body: str):
    return TWILIO_CLIENT.messages.create(
        to=to,
        from_=from_,
        body=body
    )


def lambda_handler(event, context):
    print(event)
    ############################
    # WEBHOOK VALIDATION
    ############################
    validator = RequestValidator(TWILIO_AUTH_TOKEN)
    twilio_webhook = parse_qs(event['body'])
    twilio_webhook = {k: twilio_webhook[k][0] for k in sorted(twilio_webhook)}
    # del twilio_webhook['ApiVersion']
    # del twilio_webhook['SmsMessageSid']
    # del twilio_webhook['NumSegments']

    # url = f"https://{event['headers']['Host']}{event['requestContext']['path']}"
    # print(twilio_webhook)
    # print(url)
    # print(event['headers'].get('X-Twilio-Signature'))
    # if not validator.validate(uri=url, params=twilio_webhook, signature=event['headers'].get('X-Twilio-Signature')):
    #     raise Exception('Twilio webhook validation failed')
    # decode twilio webhook
    print(twilio_webhook)
    # get the phone number from the webhook
    user_phone_number = twilio_webhook['From']
    twilio_phone_number = twilio_webhook['To']
    # get the instance id from the phone number
    db_resp = ddb_table.get_item(Key={'phone_number': user_phone_number})
    if not db_resp.get('Item'):
        # create the model instance
        instance_id = create_superpowered_model_instance(user_phone_number)
        # save the phone number / instance id mapping to dynamodb
        ddb_table.put_item(Item={'phone_number': user_phone_number, 'instance_id': instance_id})
    else:
        instance_id = db_resp['Item']['instance_id']
    
    # get the human input from the sms message and prepare for input to superpowered API /get_response endpoint
    input = {
        'prefix': user_phone_number,
        'content': twilio_webhook['Body']
    }
    # get the response from the model
    model_response = get_response_from_superpowered_model(
        instance_id=instance_id, 
        input=input
    )
    print(model_response)
    # send the response back to the user phone number
    resp = send_twilio_response(
        to=user_phone_number,
        from_=twilio_phone_number,
        body=model_response
    )

    print(resp)
    # uncomment to use the twilio webhook response format
    # return f"<?xml version=\"1.0\" encoding=\"UTF-8\"?>"\
    #        f"<Response><Message><Body>{model_response}</Body></Message></Response>"
