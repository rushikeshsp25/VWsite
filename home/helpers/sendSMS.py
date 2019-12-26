import requests
import json
from VWsite.config import *


# get request
def send_sms_number(phoneNo,textMessage):
  print(WAY2SMS_API_KEY,WAY2SMS_USETYPE,WAY2SMS_USETYPE,WAY2SMS_SENDER_ID)
  req_params = {
  'apikey':WAY2SMS_API_KEY,
  'secret':WAY2SMS_SECRET_KEY,
  'usetype':WAY2SMS_USETYPE,
  'phone': phoneNo,
  'message':textMessage,
  'senderid':WAY2SMS_SENDER_ID
  }
  return requests.post(WAY2SMS_URL, req_params)