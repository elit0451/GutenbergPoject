import csv
from pymongo import MongoClient

from pprint import pprint

client = MongoClient('mongodb://localhost:27017/')
db=client.gutenberg

def importCityData(path):
	db.geodata.delete_many({})
	# '../Resources/cities5000.csv'
	with open(path,'r',encoding='utf-8', errors='ignore') as csv_file:
		csv_reader = csv.reader(csv_file, delimiter='\t')
		geodata = []
		for row in csv_reader:
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
		print ('done importing cities')

def importBooksData(booksData):
	db.books.delete_many({})
	books = []
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
	
	print ('done importing books')


