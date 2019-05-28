import mongoImporter

def getBooks(cityName):
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


def getMentionedCities(bookTitle):
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


	
def getBooksAndCities(authorName):
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

def getBooksWithCitiesInProximity():
	books = []
	for result in mongoImporter.executeQueryAgg('geodata', pipeline4):
		books.append((result['city'], getBooks(result['city'])))
	
	for book in books:
		if(len(book[1]) > 0):
			print(book)
	return books