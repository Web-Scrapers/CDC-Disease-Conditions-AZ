from bs4 import BeautifulSoup
import requests
from random import choice
import os

# Libraries required to limit the time taken by a request
import signal
from contextlib import contextmanager

class TimeoutException(Exception): pass

@contextmanager
def time_limit(seconds):
	def signal_handler(signum, frame):
		raise TimeoutException
	signal.signal(signal.SIGALRM, signal_handler)
	signal.alarm(seconds)
	try:
		yield
	finally:
		signal.alarm(0)

BaseURL = "https://www.cdc.gov/diseasesconditions/az/{0}.html"
outDir	= "../output/"

def ckdir(dir):
	if not os.path.exists(dir):
		os.makedirs(dir)
	return

def getRequest(aurl):

	# user_agents 							= ['Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36','Mozilla/5.0 (Windows; U; Windows NT 5.1; it; rv:1.8.1.11) Gecko/20071127 Firefox/2.0.0.11','Opera/9.25 (Windows NT 5.1; U; en)','Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; .NET CLR 1.1.4322; .NET CLR 2.0.50727)','Mozilla/5.0 (compatible; Konqueror/3.5; Linux) KHTML/3.5.5 (like Gecko) (Kubuntu)','Mozilla/5.0 (Windows NT 5.1) AppleWebKit/535.19 (KHTML, like Gecko) Chrome/18.0.1025.142 Safari/535.19','Mozilla/5.0 (Macintosh; Intel Mac OS X 10.7; rv:11.0) Gecko/20100101 Firefox/11.0','Mozilla/5.0 (Macintosh; Intel Mac OS X 10.6; rv:8.0.1) Gecko/20100101 Firefox/8.0.1']
	# user_agent 							= choice(user_agents)
	user_agent 								= 'Mozzila/5.0'
	hdr 									= {'User-Agent':user_agent}

	print("Requesting website : "+aurl)
	while  True:
		try:
			try:
				with time_limit(300):
					req 	= requests.get(aurl,headers=hdr)
				break
			except TimeoutException:
				print('Request times out. Trying again...')
				continue
		except Exception as err:
			print('Error in request. Error :')
			print(err.message)
			continue
	
	return req

def getSoup(aurl):
	req 		= getRequest(aurl)
	content 	= req.content

	soup 		= BeautifulSoup(content,'html.parser')
	return soup

def scrapeConditions(url,outfile):
	soup 		= getSoup(url)
	print("Processing page...")
	results		= soup.find('div',{'class':'span16'}).find_all('li')
	for result in results:
		text 	= result.get_text().strip()
		disease = ''
		subCat 	= ''
		ref 	= ''
		link	= result.find('a')['href']

		classes = str(result.find('a')['class'])
		if "level2" in classes:
			subCat 	= text
		elif "level3" in classes:
			ref 	= text
		else:
			disease = text

		print(disease+"|"+subCat+"|"+ref+"|"+link)
		outfile.write(disease+"|"+subCat+"|"+ref+"|"+link+"\n")
	return


def begin():
	ckdir(outDir)
	outFile = outDir +"All.txt"
	outfile = open(outFile,'w')
	outfile.write("diseases|sub-category|reference|link\n")
	for i in range(0,26):
		# outFile	= outDir+chr(i+97)+".txt"
		# outfile = open(outFile,'w')
		# outfile.write("diseases|sub-category|reference|link\n")
		URL		= BaseURL.format(chr(i+97))
		scrapeConditions(URL,outfile)
	return

if __name__ == "__main__":
	begin()
	print("done")