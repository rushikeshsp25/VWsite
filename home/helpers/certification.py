def generate_cert_id(exam_code,conduct_date,entry_no):
    date=conduct_date.split('-')
    for _ in range(0,(4-len(entry_no))):
        entry_no='0'+entry_no
    cert_id='VW'+exam_code+date[2]+date[1]+date[0][2:]+entry_no
    print(cert_id)
    return cert_id