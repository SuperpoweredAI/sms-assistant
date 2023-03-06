import os
from twilio.rest import Client
import boto3
import cfnresponse
import os
import traceback


def lambda_handler(event, context):
    """
    This custom resource will create a phone number in Twilio
    """
    ############################
    # Initialize variables
    ############################
    new_props = event['ResourceProperties']
    event_type = event['RequestType']
    response_data = {}
    unique_id = 'AWS_CLOUDFORMATION#' + event['LogicalResourceId'] + '#' + event['ResourceType']

    ############################
    # Handle everything else in try/except
    ############################
    try:

        ############################
        # Get secrets from SSM
        ############################
        print(event)
        # initialize the twilio parameters
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

        webhook_url = new_props['WebhookUrl']

        ############################
        # Handle the event
        ############################
        # CREATE
        if event_type == 'Create':
            ############################
            # buy the phone number
            ############################
            new_number = TWILIO_CLIENT.incoming_phone_numbers.create(
                area_code='415',
                friendly_name=unique_id,
                sms_url=webhook_url,
                sms_method='POST'
            )
            print(new_number.__dict__)
            response_data['PhoneNumber'] = new_number.phone_number
        # UPDATE or DELETE
        else:
            ############################
            # find the phone number by the unique id
            ############################
            all_numbers = TWILIO_CLIENT.incoming_phone_numbers.list(friendly_name=unique_id, limit=2)
            assert len(all_numbers) == 1
            sid = all_numbers[0].sid
            # UPDATE
            if event_type == 'Update':
                ############################
                # update the sms url
                ############################
                updated_number = TWILIO_CLIENT.incoming_phone_numbers(sid).update(sms_url=webhook_url)
                print(updated_number.__dict__)
                response_data['PhoneNumber'] = updated_number.phone_number
            # DELETE
            elif event_type == 'Delete':
                ############################
                # delete the phone number
                ############################
                TWILIO_CLIENT.incoming_phone_numbers(sid).delete()


        ############################
        # Send a successful response
        ############################
        print("Operation successful!")
        cfnresponse.send(
            event=event,
            context=context,
            responseStatus=cfnresponse.SUCCESS,
            responseData=response_data,
            physicalResourceId=unique_id
        )

    except Exception as e:
        print("Operation failed...")
        traceback.print_exc()
        print(str(e))
        response_data['Data'] = str(e)
        ############################
        # Send a failed response
        ############################
        cfnresponse.send(
            event=event,
            context=context,
            responseStatus=cfnresponse.FAILED,
            responseData=response_data,
            physicalResourceId=unique_id
        )
