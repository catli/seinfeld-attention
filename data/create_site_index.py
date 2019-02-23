'''
    create the list of seinfeld episodes available and their associated
    urls
'''
import requests
from bs4 import BeautifulSoup
import re
import csv
import pdb


def get_page_content(page_link, timeout):
    page_response = requests.get(page_link, timeout=timeout)
    page_content = BeautifulSoup(page_response.content, "html.parser")
    return page_content


def find_all_links(content, writer):
    # find the link for example similar to:
    #     <a href="index.html">Home</a>
    tables = content.findAll('tr')
    for body in tables:
        # pdb.set_trace()
        try:
            # try to find rows in tables
            tds = body.findAll('td')
            for td in tds:
                print(td)
                try:
                    arefs = td.findAll('a')
                    for alink in arefs:
                        link = re.search(r'href=[\'"]?([^\'" >]+)', str(alink))
                        name = re.search(r'html">?([^\<>]+)', str(alink))
                        row = [link.group(1)]
                        writer.writerow(row)
                except:
                    continue
        except:
            continue


def create_index():
    page_link = "http://www.seinfeldscripts.com/seinfeld-scripts.html"
    timeout = 5
    content = get_page_content(page_link, 5)
    index_filename = "seinfield_links.csv"
    csv_writer = open(index_filename, 'w')
    episode_writer = csv.writer(csv_writer, delimiter = ',')
    alinks = find_all_links(content, episode_writer)


if __name__ == '__main__':
    create_index()

