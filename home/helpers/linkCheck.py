# from html.parser import HTMLParser
# import urllib.request as urllib2
from bs4 import BeautifulSoup
import requests

def url_ok(url):
    try:
        r = requests.head(url)
        return r.status_code == 200
    except:
        return False

def getNotWorkingLinksHtml(html_string):
    not_working_links = []
    soup = BeautifulSoup(html_string,'html.parser')
    for link in soup.findAll('a'):
        #check weather the link is working 
        #if no add it to the list
        if not url_ok(link.get('href')):
            not_working_links.append({
                "title":link.text,
                "link":link.get('href')
            })
    return not_working_links

def get_not_working_links_pdf(pdf_content):
    study_courses_pdf = StudyCourse.objects.all()
    not_working_pdf_links_all=[]
    for  course in study_courses_pdf:   
        pages = pdf_content.getNumPages()
        key = '/Annots'
        uri = '/URI'
        ank = '/A'
        for page in range(pages):
            pageSliced = pdf_content.getPage(page)
            pageObject = pageSliced.getObject()
            if key in pageObject.keys():
                ann = pageObject[key]
                for a in ann:
                    u = a.getObject()
                    if uri in u[ank].keys():
                        request = requests.get(u[ank][uri])
                        if request.status_code == 200:
                            pass
                        else:
                            #As link is not working add it to pdf links
                            not_working_pdf_links_all.append(u[ank][uri])
    return not_working_pdf_links_all