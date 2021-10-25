from smtplib import SMTPException

from django.conf import settings
from django.core.mail import send_mail

from smsapi.client import SmsAPI
from smsapi.responses import ApiError

def SendSMS (number, content):
    # Wysłanie SMS z użyciem bibliotek SMSAPI
    api = SmsAPI()
    api.reset()

    # autoryzacja za pomocą tokenu
    api.auth_token = settings.SMS_TOKEN

    try:
        api.service('sms').action('send')

        api.set_content(content)
        api.set_to(number)
        api.set_encoding('utf-8')
        api.set_normalize()
        # api.set_from('SALT Aviation')

        response = api.execute()
        result = not response.current['error']

    except ApiError:
        result = False

    return result


def SendMail (address, subject, content):
    # Wysłanie emaila do użytkownika
    try:
        response = send_mail(subject, content, settings.EMAIL_FROM, [address], fail_silently=False)
        result = (response == 1)

    except SMTPException:
        result = False

    return result


def SendMessage (fbouser, message):
    # Wysłanie wiadomości za pomocą SMS lub mail w zależności od dostępności

    sent = False
    if fbouser.telephone:
        sent = SendSMS(fbouser.telephone, message)

    if not sent and fbouser.email:
        sent = SendMail(fbouser.email, settings.EMAIL_SUBJECT , message)

    return sent