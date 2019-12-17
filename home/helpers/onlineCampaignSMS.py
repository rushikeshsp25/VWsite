import requests
import json 
from VWsite.config import *

 
def sendPostRequest(reqUrl, apiKey, secretKey, useType, phoneNo, senderId, textMessage):
    req_params = { 'apikey':apiKey, 'secret':secretKey, 'usetype':useType, 'phone': phoneNo,'message':textMessage,'senderid':senderId }
    return requests.post(reqUrl, req_params) 
 

def send_sms(file,message):
    lines=file.split('\r\n')[1:]                    #avoid headings
    for i in lines: 
        if i!='':                                 #eof check
            row=i.split(',')
            if row[1]!='':                         #blank cell check
                mobile_no=row[1]
                try:
                    response = sendPostRequest(WAY2SMS_URL, WAY2SMS_API_KEY, WAY2SMS_SECRET_KEY, WAY2SMS_USETYPE, mobile_no,WAY2SMS_SENDER_ID,message ) 
                except:
                    return 0
                d=json.loads(response.text)             #str to dict
                if d["status"] == "error":              #error while  sending message
                    return 0               
    return 1
    