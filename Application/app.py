import os
import rdflib
import mongoImporter
import neo4jImporter

from rdflib import URIRef, Graph
from geotext import GeoText
from utilities import Importer


def extractCities(text):
	places = set(GeoText(text).cities)
	
	return places
		
		

def extractGraphInfo(graph):
	title = ''
	agent = ''
	author = ''
	
	uri = rdflib.term.URIRef(u'http://purl.org/dc/terms/title')
	for o in graph.objects(subject=None, predicate=uri):
		title = o.replace('\r\n', ' ').replace('\n', ' ')
	
	uri = rdflib.term.URIRef(u'http://purl.org/dc/terms/creator')
	for o in graph.objects(subject=None, predicate=uri):
		agent = o
	
	uri = rdflib.term.URIRef(u'http://www.gutenberg.org/2009/pgterms/name')
	for o in graph.objects(subject=agent, predicate=uri):
		author = o.replace('\r\n', ' ').replace('\n', ' ')

	if(author == ''):
		author = 'Unknown'

	bookDetails = (title, author)
	return bookDetails

booksDir = '../Resources/Books'
catalogueDir = '../Resources/Offline_Catalogue'
citiesFile = '../Resources/cities5000.csv'

def runImport():
	bookPaths = os.listdir(booksDir)
	booksData = []
	bookCount = 0

	for bookFile in bookPaths:
		bookId = bookFile[:-4]
		bookCataloguePath = catalogueDir + '/' + bookId + '/pg' + bookId + '.rdf'
		
		try:
			with open(booksDir + '/' + bookFile, 'r', encoding='utf-8') as content_file:
				content = content_file.read()
				cities = extractCities(content)
			
			graph = Graph()
			graph.parse(bookCataloguePath, format = 'xml')
			
			booksData.append((extractGraphInfo(graph), cities))
		except:
			print('Error in ' + booksDir + '/' + bookFile)
		
		if(bookCount > 500):
			Importer.getInstance().updateProgress(None,True,bookCount)
			bookCount = 0
		bookCount += 1
	Importer.getInstance().updateProgress(None,True,bookCount)

	print('Finished parsing books')
	mongoImporter.importCityData(citiesFile)
	mongoImporter.importBooksData(booksData)
	neo4jImporter.loadCitiesFromCSV('cities5000.csv')
	neo4jImporter.composeBookCreate(booksData)




	

