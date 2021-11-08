import requests
import json
from amoCRM.settings import AMOCRM_ID, AMOCRM_SECRET_KEY, AMOCRM_REDIRECT_URI, AMOCRM_URI, AMOCRM_EMAIL_ID, \
    AMOCRM_PHONE_ID


def refresh_token(token, is_auth=False):
    data = get_refresh_token_data(token, is_auth)
    r = requests.post(AMOCRM_URI + '/oauth2/access_token', data=data)
    response = r.json()

    save_token('access', response['access_token'])
    save_token('refresh', response['refresh_token'])


def check_token():
    token = get_token('refresh')
    refresh_token(token)


def get_refresh_token_data(token, is_auth):
    data = {
        'client_id': AMOCRM_ID,
        'client_secret': AMOCRM_SECRET_KEY,
        'redirect_uri': AMOCRM_REDIRECT_URI,
    }

    if is_auth:
        data['grant_type'] = 'authorization_code'
        data['code'] = token
    else:
        data['grant_type'] = 'refresh_token'
        data['refresh_token'] = token

    return data


def get_contact(params):
    headers = {'Authorization': f'Bearer {get_token("access")}'}

    # Api v4 доступен только партерам AmoCRM.
    r = requests.get(f'{AMOCRM_URI}api/v3/contacts', headers=headers, params=params)
    if r.status_code == 200:
        return r.json()['_embedded']['contacts'][0]['id']


def update_contact(contact_id, name, email, phone):
    headers = {'Authorization': f'Bearer {get_token("access")}'}
    data = generate_contact_data(name, email, phone)

    requests.patch(f'{AMOCRM_URI}api/v4/contacts/{contact_id}', headers=headers, data=json.dumps(data))


def create_contact(name, email, phone):
    headers = {
        'Authorization': f'Bearer {get_token("access")}',
        'Content-Type': 'application/json',
    }
    data = [generate_contact_data(name, email, phone)]  # Должен быть передан массив

    r = requests.post(f'{AMOCRM_URI}api/v4/contacts', headers=headers, data=json.dumps(data))
    if r.status_code == 200:
        return r.json()['_embedded']['contacts'][0]['id']


def generate_contact_data(name, email, phone):
    data = {
        'name': name,
        'custom_fields_values': [
            {
                'field_id': AMOCRM_EMAIL_ID,
                'values': [
                    {
                        'value': email,
                    }
                ]
            },
            {
                'field_id': AMOCRM_PHONE_ID,
                'values': [
                    {
                        'value': phone,
                    }
                ]
            },
        ]
    }

    return data


def create_lead(contact_id):
    headers = {
        'Authorization': f'Bearer {get_token("access")}',
        'Content-Type': 'application/json',
    }

    data = [{
        '_embedded': {
            'contacts': [
                {
                    'id': contact_id
                }
            ]
        }
    }]

    requests.post(f'{AMOCRM_URI}api/v4/leads/complex', headers=headers, data=json.dumps(data))


# token_type - access или refresh
def save_token(token_type, token):
    with open(f'{token_type}_token', 'w') as f:
        f.write(token)


# token_type - access или refresh
def get_token(token_type):
    with open(f'{token_type}_token', 'r') as f:
        token = f.read()
    return token
