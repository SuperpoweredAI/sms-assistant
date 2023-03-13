import requests

BASE_URL = 'https://api.superpowered.ai/v1'
SUPERPOWERED_API_KEY_ID = '<SP API KEY ID>'
SUPERPOWERED_API_KEY_SECRET = '<SP API KEY SECRET>'

INCANTATIONS = {
    'not-repetitive': 'The conversation should not be repetitive. New topics and patterns of conversation should emerge naturally.',
    'extensive-knowledge': 'You have been trained on the entire internet and every book that has ever been written, so you have extensive knowledge on a wide variety of topics.',
    'not-just-answers': 'You should not just answer questions, but also ask questions and engage in conversation.',
}


def create_incantation(title: str, text: str) -> str:
    """ Create an incantation via the REST API and return the incantation ID. """
    resp = requests.post(
        f'{BASE_URL}/incantations',
        auth=(SUPERPOWERED_API_KEY_ID, SUPERPOWERED_API_KEY_SECRET),
        json={'title': title, 'text': text}
    )
    if not resp.status_code == 200:
        raise Exception(f'Error creating "{title}" incantation: {resp.text}')
    return resp.json()['id']


if __name__=='__main__':
    # create the incantations
    incantation_ids = [create_incantation(title, text) for title, text in INCANTATIONS.items()]
    print(incantation_ids)
    model_spec = {
        'incantation_ids': incantation_ids,
        'temperature': 'dynamic',
        'max_tokens': 500,
        'tool_names': ['Search'],
        'model_title': 'SMS Assistant',
        'ai_name': 'Alfred',
        'has_short_term_memory': True,
        'has_long_term_memory': True,
        'has_conversation_thoughts': False,
        'knowledge_bases': [],
        'agent_note_taking_config': {}
    }

    # create the model
    resp = requests.post(
        f'{BASE_URL}/models',
        auth=(SUPERPOWERED_API_KEY_ID, SUPERPOWERED_API_KEY_SECRET),
        json={'model_spec': model_spec, 'description': 'SMS Assistant from https://github.com/SuperpoweredAI/sms-assistant'}
    ).json()
    print(resp)
    print('MODEL ID FOR SMS ASSISTANT: ', resp['id'])