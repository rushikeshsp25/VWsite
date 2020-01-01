import requests
import json 
from VWsite.config import *

 
def sendPostRequest(reqUrl, apiKey, secretKey, useType, phoneNo, senderId, textMessage):
    req_params = { 'apikey':apiKey, 'secret':secretKey, 'usetype':useType, 'phone': phoneNo,'message':textMessage,'senderid':senderId }
    return requests.post(reqUrl, req_params) 
 

def send_sms(file,message):
    lines=file.split('\n')[1:]                    #avoid headings
    mobile_numbers = []
    for i in lines: 
        if i:                                 #eof check
            row=i.split(',')
            if row[1]!='':                         #blank cell check
                mobile_numbers.append(row[1])
    # insert the list to the set 
    mobile_numbers_set = set(mobile_numbers) 
    # convert the set to the list 
    unique_mobile_numbers = (list(mobile_numbers_set)) 
    error_prone_mobile_numbers = []
    for mobile_number in unique_mobile_numbers:
        try:
            response = sendPostRequest(WAY2SMS_URL, WAY2SMS_API_KEY, WAY2SMS_SECRET_KEY, WAY2SMS_USETYPE, mobile_number,WAY2SMS_SENDER_ID,message ) 
            response_text=json.loads(response.text)            #str to dict 
            if response_text["status"] == "error":              #error while  sending message
                error_prone_mobile_numbers.append(mobile_number)
        except Exception as e:
            error_prone_mobile_numbers.append(mobile_number)
    if len(error_prone_mobile_numbers):
        return {'status':0,'payload':str(error_prone_mobile_numbers)}
    return {'status':1,'payload':None}    