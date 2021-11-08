from django.http import HttpResponse
from .functions import refresh_token, get_contact, update_contact, create_contact, create_lead, check_token


def auth(request):
    auth_key = request.GET.get('code')
    refresh_token(auth_key, is_auth=True)
    return HttpResponse("OK")


def contacts(request):
    name = request.GET.get('name')
    email = request.GET.get('email')
    phone = request.GET.get('phone')

    if not name or not email or not phone:
        return HttpResponse("Bad request")

    check_token()

    email_params = {
        'filter[426411]': email
    }
    phone_params = {
        'filter[426415]': phone
    }

    contact_id = get_contact(email_params)
    if not contact_id:
        contact_id = get_contact(phone_params)

    if contact_id:
        update_contact(contact_id, name, email, phone)
    else:
        contact_id = create_contact(name, email, phone)

    create_lead(contact_id)

    return HttpResponse(contact_id)
