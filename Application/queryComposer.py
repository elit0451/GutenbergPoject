import mongoImporter
from neo4jImporter import neov

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

    results = mongoImporter.executeQueryAgg('books', pipeline1)

    for book in results:
        books.append([book['title'],book['author']])

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

    results = mongoImporter.executeQueryAgg('books', pipeline2)
    for result in results:
        if('location' in result):
            # latitude, longitude
            coordinates.append([
                result['cities'],
                result['location']['coordinates'][0], 
                result['location']['coordinates'][1]
                ])
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

def mongoQuery3Titles(results):
    titles = set()
    for result in results:
        titles.add(result['title'])
        
    return list(titles)
def mongoQuery3Cities(titles):
    cities = set()
    for title in titles:
        query1Cities = mongoQuery2(title)
        for city in query1Cities:
            cities.add((city[0], city[1], city[2]))

    return list(cities)

def mongoQuery4(long, lat, radius):
    results = []
    
    pipeline4 = [
        {         
            "$geoNear": {
            "distanceField": "location",
            "near":
            {
                "type": 'Point',
                "coordinates": [ float(long), float(lat) ]
            },
            "maxDistance": int(radius),
            "spherical": "true",
            "limit": 1000
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
        books = mongoQuery1(result['city'])
        titles = []
        for book in books:
            titles.append(book[0])
        if(len(books) > 0):
            results.append((result['city'], titles))

    return results


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
            return (neov(neoQuery1(values[0])), None)

        elif(query == '2'):
            return (neov(neoQuery2(values[0])), None)

        elif(query == '3'):
            query = neoQuery3(values[0])
            preResult = neov(query)
            result = neoQuery3Cities(preResult)
            resultExtra = neoQuery3Titles(preResult)
            return (result, resultExtra)

        elif(query == '4'):
            return (neov(neoQuery4(values[0],values[1],values[2])), None)
    elif(database == 'mongo'):
        if(query == '1'):
            return (mongoQuery1(values[0]), None)

        elif(query == '2'):
            return (mongoQuery2(values[0]), None)

        elif(query == '3'):
            preResult = mongoQuery3(values[0])
            resultExtra = mongoQuery3Titles(preResult)
            result = mongoQuery3Cities(resultExtra)

            return (result, resultExtra)

        elif(query == '4'):
            return (mongoQuery4(values[0],values[1],values[2]), None)
