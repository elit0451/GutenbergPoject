import mongoImporter
import csv
from neo4jImporter import neov
from time import time

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
    start = time()
    results = mongoImporter.executeQueryAgg('books', pipeline1)
    end = time()

    for book in results:
        books.append([book['title'],book['author']])

    return (books, end - start)

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

    start = time()
    print("started2")
    results = mongoImporter.executeQueryAgg('books', pipeline2)
    end = time()
    print("finished2")
    
    print(start)
    print(end)
    print(end - start)

    for result in results:
        if('location' in result):
            # latitude, longitude
            coordinates.append([
                result['cities'],
                result['location']['coordinates'][0], 
                result['location']['coordinates'][1]
                ])
    return (coordinates, end - start)
    
def mongoQuery3(authorName):
    cityBooks = []
    pipeline3 = [
        {
            "$match":{"$text": { "$search": authorName}}
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
                "title": 1,
                "cities": 1,
                "location": { "$arrayElemAt": ["$cityCoordinates.location", 0] },
                "_id": 0
            }
        }
    ]

    start = time()
    print("started3")
    results = mongoImporter.executeQueryAgg('books', pipeline3)
    print("finished3")
    end = time()
    
    print(start)
    print(end)
    print(end - start)

    for result in results:
        print(result)
        cityBooks.append(result)

    print(end - start)
    return (cityBooks, end - start)

def mongoQuery3Titles(results):
    titles = set()
    for result in results:
        titles.add(result['title'])
        
    return list(titles)

def mongoQuery3Cities(titles):
    cities = set()
    totalTime = 0

    for title in titles:
        query1Cities, queryTime = mongoQuery2(title)
        totalTime += queryTime

        for city in query1Cities:
            cities.add((city[0], city[1], city[2]))

    return (list(cities), totalTime)

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
    start = time()
    queryResults = mongoImporter.executeQueryAgg('geodata', pipeline4)
    end = time()

    totalTime = end - start

    for result in queryResults:
        books, queryTime = mongoQuery1(result['city'])
        totalTime += queryTime
        titles = []
        for book in books:
            titles.append(book[0])
        if(len(books) > 0):
            results.append((result['city'], titles))

    return (results, totalTime)


def neoQuery1(city):
    start = time()
    result = neov('''match (b:Book)-[:MENTIONS]-(c:City {name: "''' + str(city) + '''"})
            return b.title, b.author''')
    end = time()

    return (result, end - start)

def neoQuery2(title):
    start = time()
    result = neov('''match (:Book {title:"''' + str(title) + '''"})-[:MENTIONS]-(c:City)
            return c.name, c.long,c.latt''')
    end = time()

    return (result, end - start)

def neoQuery3(author):
    start = time()
    result = neov('''match (b:Book {author:"''' + author + '''"})-[:MENTIONS]-(c:City)
                        return b.title, collect(c)''')
    end = time()

    return (result, end - start)

def neoQuery3Titles(results):
    titles = set()
    for result in results:
        titles.add(result[0])
        
    return list(titles)

def neoQuery3Cities(results):
    cities = set()
    for result in results:
        for city in result[1]:
            cities.add((city['name'], city['long'], city['latt']))
    return list(cities)

def neoQuery4(long, lat, radius):
    start = time()
    result = neov('''MATCH (city:City)
            WITH point({ x: city.long, y: city.latt, crs: 'WGS-84' }) AS p1, point({ x: ''' + long + ''' , y: ''' + lat + ''', crs: 'WGS-84' }) AS p2, city
            WHERE distance(p1,p2) < ''' + radius + '''
            WITH city
            MATCH (b:Book)-[:MENTIONS]-(c:City)
            WHERE id(c) = id(city)
            RETURN c.name, collect(b.title)''')
    end = time()

    return (result, end - start)


def writeToCSV(queryNr, db, time):
    with open('Timings.csv','a') as csvFile:
        if(db == 'mongo'):
            csvStr = ',' + queryNr + ',' + db + ',' + time
        elif(db == 'neo4j'):
            csvStr = '\n' + queryNr + ',' + db + ',' + time
        csvFile.write(csvStr)
        print(csvStr)
        csvFile.close() 
        print('Done writing')

def executeQuery(database, query, values):
    if(database == 'neo4j'):
        if(query == '1'):
            result, time = neoQuery1(values[0])
            writeToCSV(query, database, str(time)[:7])
            return (result, None, str(time)[:7])

        elif(query == '2'):
            result, time = neoQuery2(values[0])
            writeToCSV(query, database, str(time)[:7])
            return (result, None, str(time)[:7])

        elif(query == '3'):
            execQuery, time = neoQuery3(values[0])
            result = neoQuery3Cities(execQuery)
            resultExtra = neoQuery3Titles(execQuery)
            writeToCSV(query, database, str(time)[:7])
            return (result, resultExtra, str(time)[:7])

        elif(query == '4'):
            result, time = neoQuery4(values[0], values[1],values[2])
            writeToCSV(query, database, str(time)[:7])
            return (result, None, str(time)[:7])
            
    elif(database == 'mongo'):
        if(query == '1'):
            result, time = mongoQuery1(values[0])
            writeToCSV(query, database, str(time)[:7])
            return (result, None, str(time)[:7])

        elif(query == '2'):
            result, time = mongoQuery2(values[0])
            writeToCSV(query, database, str(time)[:7])
            return (result, None, str(time)[:7])

        elif(query == '3'):
            preResult, time = mongoQuery3(values[0])
            resultExtra = mongoQuery3Titles(preResult)
            print(resultExtra)
            result, queryTime = mongoQuery3Cities(resultExtra)
            writeToCSV(query, database, str(time + queryTime)[:7])
            return (result, resultExtra, str(time + queryTime)[:7])

        elif(query == '4'):
            result, time = mongoQuery4(values[0],values[1],values[2])
            writeToCSV(query, database, str(time)[:7])
            return (result, None, str(time)[:7])
           
