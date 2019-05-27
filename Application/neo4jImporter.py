import sys
import csv

from neo4j import GraphDatabase, Transaction

uri = 'bolt://localhost:7687'
auth=('neo4j', 'secur3P4ss')

# function to execute queries in Neo4j
def neo(command, driver):
    try:
        with driver.session() as session:
            result = session.run(command)
        return result # result is a resultset/cursor for neo4j
    except Exception as ex:
        print(ex, file=sys.stderr)
        
def neov(command):
    driver = getNeoDriver()
    result = neo(command, driver).values()
    driver.close()
    return result

def getNeoDriver():
    try:
        driver = GraphDatabase.driver(uri, auth=auth)
        return driver
    except Exception as exception:
        return 'Something went wrong - ' + str(exception)

def composeBookCreate(booksData):
    deleteAllBooks()
    driver = getNeoDriver()
    count = 0
    try:
        with driver.session() as session:
            transaction = session.begin_transaction()

            for data in booksData:
                # data - tuple of (tuple of title and author) and cities
                title = data[0][0]
                author = data[0][1]
                cities = ','.join('\'' + str(city) + '\'' for city in data[1])
                query = bookQuery.replace('$$cities$$', cities)

                transaction.run(query, {"title": title, "author": author})
                count += 1

                if(count > 100):
                    transaction.commit()
                    count = 0
                    transaction = session.begin_transaction()

            transaction.commit()

        driver.close()
        print('Finished importing books in Neo4j')
    except Exception as exception:
        print('Something went wrong while inserting books - ' + str(exception))    

def loadCitiesFromCSV(path):
    # cities5000.csv
    deleteAllCities()
    constraintQuery = 'CREATE CONSTRAINT ON (city:City) ASSERT city.name IS UNIQUE'
    query = '''
    LOAD CSV FROM "file:///''' + path + '''" AS row 
    FIELDTERMINATOR "\t"
    WITH row
    WHERE NOT row[2] IS NULL
    MERGE (city :City {name:row[2]})
    SET
    city.latt = toFloat(row[4]), 
    city.long = toFloat(row[5])
    '''
    neov(constraintQuery)
    neov(query)
    print('Finished importing cities in Neo4j')   

def deleteAllCities():
    query = '''
    MATCH (city:City) DETACH DELETE city
    '''
    neov(query)
    print('All cities are deleted')  

def deleteAllBooks():
    query = '''
    MATCH (book:Book) DETACH DELETE book
    '''
    neov(query)
    print('All books are deleted')  

bookQuery = '''
CREATE (book:Book {title:{title}, author:{author}})
WITH [$$cities$$] AS cities, book
UNWIND cities AS city
MATCH (c:City {name:city})
WITH c, book
CREATE (book)-[:MENTIONS]->(c)
'''