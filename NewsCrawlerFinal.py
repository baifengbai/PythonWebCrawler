from bs4 import BeautifulSoup as BS
from time import sleep
from datetime import datetime
import requests
import mysql.connector

# class for getting html data from website and making a 'soup' of it to be analyzed
class Crawly:

	_parser = 'lxml'
	links_list = []
	titles_list = []	

	def __init__(self, address):
		self.address = address
		res = requests.get(self.address)
		self.soup = BS(res.text, self._parser)

	# re-gets the site we grab the news from
	def reinitialize(self):
		res = requests.get(self.address)
		self.soup = BS(res.text, self._parser)

# class for doing functions with two parameters
class FunctionDriver:
	
	def __init__(self, function, function_parameter1, function_parameter2):
		self._myfunction = function
		self._parameter_1 = function_parameter1
		self._parameter_2 = function_parameter2

	# self-explanatory
	def doFunction(self):
		self._myfunction(self._parameter_1, self._parameter_2)

# class for - you guessed it - handling database events used in this program
class DatabaseHandler:

	# connects to database
	def __init__(self):
		self._mydb = mysql.connector.connect(
			host="hostname",
			user="user",
			passwd="pw",
			database="crawler-results"
		) 
		self._mycursor = self._mydb.cursor()

	# modifies top 5 articles of a news site
	# old most popular news are therefore discarded - they are not needed to be kept for this project					
	def updateTopFive(self, links_list, titles_list, links_column_name, titles_column_name):
		for i in range(5):
			query = "UPDATE popularnews SET {} = '{}', {} = '{}' WHERE popularity = {};"
			query = query.format(links_column_name, links_list[i], titles_column_name, titles_list[i], (i+1))
			self._mycursor.execute(query)
			self._mydb.commit()
		print("Updated top 5 articles of a news site")

	# updates completion time of latest search
	def updateTime(self):
		dt_string = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
		query = "UPDATE popularnews SET timestring = '%s' WHERE popularity = 1;" % dt_string
		self._mycursor.execute(query)
		self._mydb.commit()
		print("Updated completion time of latest search")


# gets most popular news from Iltalehti and updates them into database
def iltalehtiFunction(il,db):
	links_list = []
	titles_list = []

	data = il.soup.find('div', attrs={'class':'article-list'})
	a_data = data.findAll('a')
	for stuff in a_data:
		links_list.append(il.address+stuff['href'])
		titles_list.append(stuff.text)
	print("Found " + str(len(links_list)) + " links, " +str(len(titles_list)) + " popular news items at "+ il.address)

	db.updateTopFive(links_list, titles_list, "il_links", "il_titles")


# gets most popular news from Kaleva and updates them into database
def kalevaFunction(kaleva,db):
	links_list = []
	titles_list = []

	data = kaleva.soup.findAll('dl', attrs={'class':'widget__news-stream-popular'})
	for stuff in data:
		links = stuff.findAll('a')
		titles = stuff.findAll('span', attrs={'class':'primary-content__link common_newsarticle'})
		for l in links:
			links_list.append(kaleva.address+l['href'])
		for t in titles:
			titles_list.append(t.text.strip())
	print("Found " + str(len(links_list)) + " links, " +str(len(titles_list)) + " popular news items at "+ kaleva.address)

	db.updateTopFive(links_list, titles_list, "kaleva_links", "kaleva_titles")


# gets most popular news from Kouvolan Sanomat and updates them into database
def kouvolaFunction(ks,db):
	links_list = []
	titles_list = []  

	data = ks.soup.find('div', attrs={'class':'articles textual'})
	a_data = data.findAll('a')
	for stuff in a_data:
		links_list.append(ks.address+stuff['href'])
		titles_list.append(stuff['title'])
	print("Found " + str(len(links_list)) + " links, " +str(len(titles_list)) + " popular news items at "+ ks.address)

	db.updateTopFive(links_list, titles_list, "ks_links", "ks_titles")

	
if __name__ == "__main__":

	db = DatabaseHandler()
	il = Crawly('https://www.iltalehti.fi')
	kaleva = Crawly('https://www.kaleva.fi')
	ks = Crawly('https://www.kouvolansanomat.fi')

	functions = [FunctionDriver(iltalehtiFunction,il,db), FunctionDriver(kalevaFunction,kaleva,db), FunctionDriver(kouvolaFunction,ks,db)]
	crawlers = [il, kaleva, ks]

	while True:	

		# calls crawler functions...
		# these functions handle getting info from the web and inserting it into a database
		for function in functions:
			function.doFunction()

		# updates completion time of latest crawl
		db.updateTime()
			
		# wait 30 minutes before updating results
		sleep(1800)

		# get latest data from web
		for crawler in crawlers:
			crawler.reinitialize()

		print(" ")

	

