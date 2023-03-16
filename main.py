#!/usr/bin/env python3
import requests
import re
import os
import io
import ocrmypdf
import base64
import tempfile
import img2pdf
from bs4 import BeautifulSoup

BASE_URL = 'https://aip.dfs.de/basicVFR/'

images = []

def fetch_folder(foldertitle, folderurl, depth = 0):
	#print(folderurl)
	response = requests.get(folderurl)
	html = BeautifulSoup(response.text, 'lxml')
	items = html.main.find_all('a', class_=['folder-link', 'document-link'])

	for item in items:
		if 'folder-link' in item['class']:
			title = item.find(class_='folder-name', attrs={'lang': 'en'}).text
			print(title)
			fetch_folder(title, requests.compat.urljoin(BASE_URL, item.get('href')), depth + 1)
		if 'document-link' in item['class']:
			documenttitle = item.find(class_='document-name', attrs={'lang': 'en'}).text
			print(f'  {documenttitle}')
			fetch_document(documenttitle, requests.compat.urljoin(BASE_URL, item.get('href')))

		if depth == 0:
			generate_pdf(title.strip())

def fetch_document(documenttitle, documenturl):
	global images
	#print(documenturl)
	response = requests.get(documenturl)
	html = BeautifulSoup(response.text, 'lxml')
	#print(response.status_code)
	image = html.main.find('img', id='imgAIP').get('src')
	imagedata = image.split('data:image/png;base64,')[1]
	images.append(base64.decodebytes(imagedata.encode('ascii')))

def generate_pdf(title):
	global images
	tmp = tempfile.NamedTemporaryFile(suffix='.pdf')
	tmp.write(img2pdf.convert(images))
	ocrmypdf.ocr(input_file=tmp.name, output_file=f'output/{title}.pdf')
	tmp.close()
	images = []

response = requests.get(BASE_URL)
html = BeautifulSoup(response.text, 'lxml')
# The original base URL redirects to the current version of the AIP
BASE_URL = response.url

fetch_folder("AIP", BASE_URL)
