from logging import exception
from kavenegar import *


def send_sms(receptor, message):
    api = KavenegarAPI('65434E693963697457785577566D49636D666F67796F514A38335869644F71676F41712F4333564B6D58553D')

    full_message = f"""
    مشتری گرامی، دستگاه شما به شماره پذیرش {receptor.reception_no} در وضعیت {message} قرار گرفت.\n تاپ کامپیوتر.\nلغو۱۱
    """
    params = {'sender': [2000500666, 10008663], 'receptor': receptor.customer.phone, 'message': full_message}
    api.sms_send(params)


