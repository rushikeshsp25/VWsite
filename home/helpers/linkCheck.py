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

def getNotWorkingLinks(html_string):
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