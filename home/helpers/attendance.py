import json

def get_attendance_dictionary(student_list,absent_list):
    att_dict={}
    for student in student_list:
        if str(student.id) in absent_list:
            att_dict[student.id]='A'
        else:
            att_dict[student.id]='P'
    return json.dumps(att_dict)