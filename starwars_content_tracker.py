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

url='https://starwars.fandom.com/wiki/List_of_books'
running_list = file_to_list(config.working_dir + "currenttotal.txt")

try:
	response = requests.get(url)
except:
	msg = MIMEMultipart()
	msg['From'] = config.fromaddr
	msg['To'] = config.toaddr
	msg['Subject'] = "Star Wars Issue!"
	body = "There was an issue pulling the website"
	msg.attach(MIMEText(body, 'plain'))
	s = smtplib.SMTP('smtp.gmail.com', 587)
	s.ehlo()
	s.starttls()
	s.login(config.fromaddr, config.google_app)
	text = msg.as_string()
	s.sendmail(config.fromaddr, config.toaddr, text)
	s.quit()
	sys.exit(0)
	

soup = BeautifulSoup(response.text, 'lxml')

site = soup.find_all(['h2', 'h3', 'li', 'h4'])
novels = False
canon = False
legends = False
skip = False
canon_novels = []
legends_novels = []
for tag in site:
	if (not 'Canon' in tag.get_text()) and (not 'Legends' in tag.get_text()) and ('Edit' in tag.get_text()):
		skip = True
	else:
		skip = False
	if 'NovelsEdit' in tag.get_text():
		novels = True
	if 'CanonEdit' in tag.get_text():
		canon = True
	if 'LegendsEdit' in tag.get_text():
		canon = False
		legends = True
	if novels and canon and (not skip) and (not tag.get_text().strip() == 'CanonEdit'):
		if tag.get_text().strip():
			canon_novels.append(tag.get_text().strip())
	if novels and legends and (not skip) and (not tag.get_text().strip() == 'LegendsEdit'):
		if tag.get_text().strip():
			legends_novels.append(tag.get_text().strip())
	if 'Short storiesEdit' in tag.get_text():
		break

if len(running_list) > 0 and os.path.exists(config.working_dir + "currenttotal.txt"):
	os.remove(config.working_dir + "currenttotal.txt")


new_old = open(config.working_dir + "currenttotal.txt", "a+")
for c in canon_novels:
	print(c, file = new_old)
for c in legends_novels:
	print(c, file = new_old)
	

canon_content_added = []
legend_content_added = []
for content in canon_novels:
	if not content in running_list:
		canon_content_added.append(content)
for content in legends_novels:
	if not content in running_list:
		legend_content_added.append(content)

content_removed = []
for content in running_list:
	if content:
		if (not content in canon_novels) and (not content in legends_novels):
			content_removed.append(content)


if len(canon_content_added) > 0 or len(legend_content_added) > 0 or len(content_removed) > 0:
	#there has been a change
	if len(canon_content_added) > 0:
		book_body = ""
		for book in canon_content_added:
			book_body = book_body + "\r\n" + book
		body = "There was Canon content added:\r\n"+book_body
		send_mail(body)
	if len(legend_content_added) > 0:
		book_body = ""
		for book in legend_content_added:
			book_body = book_body + "\r\n" + book
		body = "There was Legends content added\r\n"+book_body
		send_mail(body)
	if len(content_removed) > 0:
		book_body = ""
		for book in content_removed:
			book_body = book_body + "\r\n" + book
		body = "There was content removed\r\n"+book_body
		send_mail(body)