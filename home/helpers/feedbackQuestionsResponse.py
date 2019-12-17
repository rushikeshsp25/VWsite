def feedback_question_responses(questions,response):
    comment_response={}
    rating_response={}
    for question in questions:
        if question.question_type=='rating':
            question_response=response.filter(question_id=question.id)
            data={'1':0,'2':0,'3':0,'4':0,'5':0}
            for i in question_response:
                if i.response in data.keys():                                     #convert ratings into dictionary format{'rate':'No of students'}
                    data[i.response]=data[i.response]+1
            rating_response[question.id]=data
        else:
            question_response=response.filter(question_id=question.id)
            l=[]
            for i in question_response:
                l.append(i.response)
            comment_response[question.id]=l
    return rating_response,comment_response