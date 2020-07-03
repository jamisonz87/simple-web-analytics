from flask import Flask, render_template, request
from bs4 import BeautifulSoup
import requests
import re

app = Flask(__name__)

@app.route('/', methods=['POST', 'GET'])
def index():
    url_error = ''
    tags = {}
    a_tag_broken_list = []
    all_links = ''
    all_scripts = ''

    site_url = ''
    
    if request.method == 'POST':
        (site, site_url) = check_url_type(request.form['webpage'])

        soup = BeautifulSoup(site.content, 'html.parser')

        all_links = soup.find_all('link', rel="stylesheet")
        all_scripts = soup.find_all('script', src=re.compile(".*"))
        
        tags = find_num_of_tags(soup)
        a_tag_broken_list = broken_links(soup, site_url)

    return render_template('index.html', url_error=url_error, tags=tags, a_tag_broken_list=a_tag_broken_list, 
                            all_links=all_links, all_scripts=all_scripts, site_url=site_url)

if __name__ == '__main__':
    app.run(debug=True)

def check_url_type(request_url):
    site = ''
    site_url = ''

    check_http = re.search("http", str(request_url))
    check_www = re.search("www", str(request_url))

    if check_http:
        site = requests.get(request_url)
        site_url = str(request.form['webpage'])
    elif check_www:
        site = requests.get('http://{}'.format(request_url))
        site_url = 'https://'+str(request_url)
    else:
        site = requests.get('http://www.{}'.format(request_url))
        site_url = 'https://www.'+str(request_url)

    return (site, site_url, )

def find_num_of_tags(soup):
     p = len(soup.find_all('p'))
     a = len(soup.find_all('a'))
     div = len(soup.find_all('div'))
     span = len(soup.find_all('span'))

     return {'p':p,'a':a,'div':div,'span':span}

def broken_links(soup, site_url):
    broken_lists = []

    for a in soup.find_all('a', href=True):
        check_url = re.search('http', str(a['href']))

        results = ''

        if check_url:
            site = a['href']
            results = requests.get(site)
            if results.status_code != 200 and results.status_code != 406 and results.status_code != 403 and results.status_code != 429:
                 broken_lists.append(site)
        else:
            site = site_url + a['href']
            results = requests.get(site)
            if results.status_code != 200 and results.status_code != 406 and results.status_code != 403 and results.status_code != 429:
                 broken_lists.append(site)

    return broken_lists

        