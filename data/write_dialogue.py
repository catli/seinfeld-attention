'''
    iterate through a url and write the dialogue
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


def write_lines(content, writer):
    # find the link for example similar to:
    #     <a href="index.html">Home</a>
    #content_div = content.findAll('div', id = 'content')
    paragraphs = content.findAll('p')
    at_comedy_club = False
    for line in paragraphs:
        # print(line)
        # check if scene is starting
        scene = re.search("Scene?([^\]]+)",str(line))
        if scene:
            # update whehther we're in comedy club
            at_comedy_club = 'comedy club' in scene[0].lower()
            if not at_comedy_club:
                row = str(scene[0])
                row_no_space = re.sub('\n', '', row)
                writer.writerow([row_no_space])
            continue
        if not at_comedy_club:
            speaker_val = re.search(r"([A-Z][a-zA-Z]+)\:",str(line.contents))
            if speaker_val:
                speaker = speaker_val[1]
                try:
                    dialogue =  re.search(r"[A-Z]+:(.*)",str(line.contents))[1]
                except:
                    pdb.set_trace()
                formatted_line = format_line_into_array(dialogue)
                dialogue_no_tab = re.sub('\t', '', dialogue)
                writer.writerow([speaker]+formatted_line)

# logic for writing the sentences into array
def format_line_into_array(dialogue):
    line = []
    word = ""
    # iterate through each letter
    last_char = ""
    commentary = False
    for char in str(dialogue):
        # if space or n and last char is /, then store word, and reset
        if (char == " ") | (last_char=="\\" and char == "n"):
            if len(word)>0:
                line.append(word)
                word = ""
        else:
            # if open bracket, then holdl on writing
            if re.match("[\[\(]", char):
                commentary = True
                if len(word)>0:
                    line.append(word)
                    word = ""
            if not commentary:
                # if punctuation, then store into line
                if re.match("[.,?;!]",char ):
                    line.append(word)
                    line.append(char)
                    word = ""
                # if not brackets and alphanumeric, then store into word
                if re.match("[A-Za-z\-]", char):
                    word = word + char
            if re.match("[\]\)]", char):
                # end of commentary
                commentary = False
        last_char = char
    return line

def write_all_lines(uri, site):
    # uri = 'TheSeinfeldChronicles.htm'
    # site = 'http://www.seinfeldscripts.com/'
    episode_link = site + uri
    write_filename = 'episodes/episode_%s' % str(uri.split('.')[0])
    csv_writer = open(write_filename, 'w')
    dialogue_writer = csv.writer(csv_writer, delimiter = '\t')

    content = get_page_content(episode_link, timeout = 5)
    write_lines(content, dialogue_writer)


def write_all_episodes():
    link_reader = open('seinfield_links.csv','r')
    site = 'http://www.seinfeldscripts.com/'
    for uri in link_reader:
        print(uri)
        uri_stripped = uri.strip()
        write_all_lines(uri_stripped, site)


if __name__ == '__main__':
    write_all_episodes()
