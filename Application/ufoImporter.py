import os
import rdflib
import mongoImporter
import neo4jImporter
import csv

from pymongo import MongoClient, TEXT, GEOSPHERE
from pprint import pprint
from utilities import Importer
from rdflib import URIRef, Graph
from geotext import GeoText
from utilities import Importer

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
		
		if(bookCount > 50):
			Importer.getInstance().updateProgress(None,True,bookCount)
			bookCount = 0
		bookCount += 1
	Importer.getInstance().updateProgress(None,True,bookCount)

	print('Finished parsing books')
	importCityData(citiesFile)
	importBooksData(booksData)

client = MongoClient('mongodb://localhost:27017/')
db=client.gutenberg

def importCityData(path):
	db.geodata.delete_many({})
	db.geodata.drop_indexes()
	db.geodata.create_index([('city', TEXT)], name='city_index', default_language='english')
	db.geodata.create_index([('location', GEOSPHERE)], name='location_index')
	# '../Resources/cities5000.csv'
	with open(path,'r',encoding='utf-8', errors='replace') as csv_file:
		csv_reader = csv.reader(csv_file, delimiter='\t')
		count = 0
		geodata = []
		for row in csv_reader:
			if(row[4] != '' and row[5] != ''):
			# coordinates: [longitude, latitude]
				datum = {
					'city':str(row[2]),
					'location':{
						'type': 'Point',
						'coordinates': [float(row[5]), float(row[4])]
					}
				}

                
				geodata.append(datum)
				if(len(geodata) > 500):
					db.geodata.insert_many(geodata)
					geodata.clear()
				if(count > 500):
					Importer.getInstance().updateProgress('mongo',False,count)
					count = 0
				count += 1
		db.geodata.insert_many(geodata)
		Importer.getInstance().updateProgress('mongo',False,count)
		print ('Finished importing cities')

def importBooksData(booksData):
	db.books.delete_many({})
	books = []
	count = 0
	for data in booksData:
		book = {
			# data - tuple of (tuple of title and author) and cities
			'title': data[0][0],
			'author': data[0][1],
			'cities': list(data[1])
		}
		books.append(book)
		if(len(books) > 500):
			db.books.insert_many(books)
			books.clear()
		if(count > 500):
			Importer.getInstance().updateProgress('mongo',True,count)
			count = 0
		count += 1
	db.books.insert_many(books)
	Importer.getInstance().updateProgress('mongo',True,count)
	
	print ('Finished importing books')

def executeQueryAgg(collection, query):
	if(collection == 'books'):
		return db.books.aggregate(query)
	elif(collection == 'geodata'):
		return db.geodata.aggregate(query)