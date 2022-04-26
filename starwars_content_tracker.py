#jared wilson

import requests
import lxml.html as lh
import pandas as pd
from bs4 import BeautifulSoup
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import config
import sys
import os
import re
import time

def file_to_list(path):
	if os.path.exists(path) and os.path.getsize(path) > 0:
		new_file = open(path,'r')
		new_list = list(new_file.read().split('\n'))
		new_file.close()
		return new_list
	else:
		return []

def send_mail(send_body):
	msg = MIMEMultipart()
	msg['From'] = config.fromaddr
	msg['To'] = config.toaddr
	msg['Subject'] = "Star Wars Content Change!"
	body = send_body
	msg.attach(MIMEText(body, 'plain'))
	s = smtplib.SMTP('smtp.gmail.com', 587)
	s.ehlo()
	s.starttls()
	s.login(config.fromaddr, config.google_app)
	text = msg.as_string()
	s.sendmail(config.fromaddr, config.toaddr, text)
	s.quit()
	time.sleep(1)
    
def send_error_mail(body):
	msg = MIMEMultipart()
	msg['From'] = config.fromaddr
	msg['To'] = config.toaddr
	msg['Subject'] = "Star Wars Issue!"
	body = "There was an issue " + body
	msg.attach(MIMEText(body, 'plain'))
	s = smtplib.SMTP('smtp.gmail.com', 587)
	s.ehlo()
	s.starttls()
	s.login(config.fromaddr, config.google_app)
	text = msg.as_string()
	s.sendmail(config.fromaddr, config.toaddr, text)
	s.quit()
	sys.exit(0)
   
def parse_current_collection():
    URL = 'https://starwars.fandom.com/wiki/List_of_books'
    running_list = file_to_list(config.working_dir + "currenttotal_released.txt")

    try:
        response = requests.get(URL)
    except:
        send_error_mail("pulling the current collection website.")
	
    soup = BeautifulSoup(response.text, 'lxml')
    
    #parse the TOC
    tag = soup.find('div', {'class' : 'toc'})
    links = tag.findAll('a')
    top_level = []
    for link in links:
        if re.match('\d\s.*', link.text):
            top_level.append(link.text[2:])
    
    #pull all novels (young and old)
    site = soup.find_all(['h2', 'h3', 'li', 'h4'])
    novels = False
    novel_list = []
    for tag in site:
        if tag.text == "Novels[]":
            novels = True
            continue
        if (novels == True) and ( not (tag.text[:-2] in top_level)):
            novel_list.append(tag.text)
        elif (novels == True) and (tag.text[:-2] in top_level):
            novels = False

    
    with open(config.working_dir + 'currenttotal_released.txt', "w") as clear:
        clear.write("")
    with open(config.working_dir + 'currenttotal_released.txt', "a+") as repopulate:
        for novel in novel_list:
            print(novel, file=repopulate)
        
    additional_novels = []
    for novel in novel_list:
        if novel not in running_list:
            additional_novels.append(novel)
    
    removed_novels = []
    for novel in running_list:
        if novel not in novel_list:
            removed_novels.append(novel)

    return additional_novels, removed_novels


def parse_future_collection():
    URL = "https://starwars.fandom.com/wiki/List_of_future_books"

    running_list = file_to_list(config.working_dir + "currenttotal_unreleased.txt")

    try:
        response = requests.get(URL)
    except:
        send_error_mail("pulling the current collection website.")

    soup = BeautifulSoup(response.text, 'lxml')
    table = soup.find_all('tr')
    upcoming_novel = []
    for line in table:
        if 'novel' in  line.get_text() or 'Novel' in  line.get_text() :
            sections = line.find_all('td')
            novel = "| "
            for entry in sections:
                novel = novel + re.sub('\n', '', entry.text) + " | "
            novel = novel.strip()
            upcoming_novel.append(novel)
    
    with open(config.working_dir + 'currenttotal_unreleased.txt', "w") as clear:
        clear.write("")
    with open(config.working_dir + 'currenttotal_unreleased.txt', "a+") as repopulate:
        for novel in upcoming_novel:
                print(novel, file=repopulate)
        
    additional_upcoming_novels = []
    for novel in upcoming_novel:
        if novel not in running_list:
            additional_upcoming_novels.append(novel)
    
    removed_upcoming_novels = []
    for novel in running_list:
        if novel not in upcoming_novel:
            removed_upcoming_novels.append(novel)
    
    return additional_upcoming_novels, removed_upcoming_novels        
        
    
if __name__ == '__main__':
    additional_novels, removed_novels = parse_current_collection()
    additional_upcoming_novels, removed_upcoming_novels = parse_future_collection()
    
    if '' in additional_novels:
        additional_novels.remove('')
    if '' in removed_novels:
        removed_novels.remove('')
    if '' in additional_upcoming_novels:
        additional_upcoming_novels.remove('')
    if '' in removed_upcoming_novels:
        removed_upcoming_novels.remove('')
    
    if len(additional_novels) > 0 or len(removed_novels) > 0 or len(additional_upcoming_novels) > 0 or len(removed_upcoming_novels) > 0:
        #there has been a change
        if len(additional_novels) > 0:
            book_body = ""
            for book in additional_novels:
                book_body = book_body + re.sub('\[\]', '', book) + "\r\n"
            body = "There were novels released!\r\n\r\n" + book_body
            send_mail(body)
        if len(removed_novels) > 0:
            book_body = ""
            for book in removed_novels:
                book_body = book_body + re.sub('\[\]', '', book) + "\r\n"
            body = "There were novels removed!\r\n\r\n" + book_body
            send_mail(body)
        if len(additional_upcoming_novels) > 0:
            book_body = ""
            for book in additional_upcoming_novels:
                book_body = book_body + re.sub('\[\]', '', book) + "\r\n"
            body = "There are new novels planned to be released!\r\n\r\n" + book_body
            send_mail(body)
        if len(removed_upcoming_novels) > 0:
            book_body = ""
            for book in removed_upcoming_novels:
                book_body = book_body + re.sub('\[\]', '', book) + "\r\n"
            body = "Some novels have been removed from the future book list!\r\n\r\n" + book_body
            send_mail(body)
