import mongoImporter
import neo4jImporter

def mongoQuery1(cityName):
	books = []
	pipeline1 = [
		{
			"$match":{"cities": cityName}
		},
		{
			"$project":{
				"title": 1,
				"author": 1,
				"_id": 0
			}
		}
	]

	for result in mongoImporter.executeQueryAgg('books', pipeline1):
		books.append(result)
	return books	


def mongoQuery2(bookTitle):
    coordinates = []
    pipeline2 = [
        {
            "$match":{"title": bookTitle}
        },
        {
            "$unwind": "$cities"
        },
        {
            "$lookup":
            {
                "from": "geodata",
                "localField": "cities",
                "foreignField": "city",
                "as": "cityCoordinates"
            }
        },
        {
            "$project":{
                "cities": 1,
                "location": { "$arrayElemAt": ["$cityCoordinates.location", 0] },
                "_id": 0
            }
        }
    ]

    for result in mongoImporter.executeQueryAgg('books', pipeline2):
        if('location' in result):
            # latitude, longitude
            coordinates.append(str(result['location']['coordinates'][0]), str(result['location']['coordinates'][1]))
    return coordinates        


	
def mongoQuery3(authorName):
    cityBooks = []
    pipeline3 = [
        {
            "$match":{"author": authorName}
        },
        {
            "$project":{
                "title": 1,
                "cities": 1,
                "_id": 0
            }
        }
    ]

    for result in mongoImporter.executeQueryAgg('books', pipeline3):
        cityBooks.append(result)
    return cityBooks    


def mongoQuery4():
    books = []
    pipeline4 = [
        {         
            "$geoNear": {
            "distanceField": "location",
            "near":
            {
                "type": 'Point',
                "coordinates": [ -8.61099, 41.14961 ]},
                "maxDistance": 200000
            }
        },
        {
            "$project":{
                "city": 1,
                "_id": 0
            }
        }
    ]

    for result in mongoImporter.executeQueryAgg('geodata', pipeline4):
        books.append((result['city'], mongoQuery1(result['city'])))
	
    for book in books:
        if(len(book[1]) > 0):
            print(book)
    return books


def neoQuery1(city):
    return '''match (b:Book)-[:MENTIONS]-(c:City {name: "''' + str(city) + '''"})
            return b.title, b.author'''
def neoQuery2(title):
    return '''match (:Book {title:"''' + str(title) + '''"})-[:MENTIONS]-(c:City)
            return c.name,c.long,c.latt'''
def neoQuery3(author):
    return '''match (b:Book {author:"''' + author + '''"})-[:MENTIONS]-(c:City)
                        return b.title, collect(c)'''
def neoQuery3Titles(results):
    titles = set()
    for result in results:
        titles.add(result[0])
        
    return list(titles)

def neoQuery3Cities(results):
    cities = set()
    for result in results:
        for city in result[1]:
            cities.add((city['name'],city['long'],city['latt']))
    
    return list(cities)

def neoQuery4(long, lat, radius):
    return '''MATCH (city:City)
            WITH point({ x: city.long, y: city.latt, crs: 'WGS-84' }) AS p1, point({ x: ''' + long + ''' , y: ''' + lat + ''', crs: 'WGS-84' }) AS p2, city
            WHERE distance(p1,p2) < ''' + radius + '''
            WITH city
            MATCH (b:Book)-[:MENTIONS]-(c:City)
            WHERE id(c) = id(city)
            RETURN c.name, collect(b.title)'''    

def executeQuery(database, query, values):
    if(database == 'neo4j'):
        if(query == '1'):
            return neoQuery1(values[0])
