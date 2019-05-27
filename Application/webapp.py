#!/usr/bin/python3

import mongoImporter
from neo4jImporter import neov
from utilities import createMap

from flask import Flask,render_template, request,jsonify,Response

app = Flask(__name__)



def getQuery1(city):
    return '''match (b:Book)-[:MENTIONS]-(c:City {name: "''' + str(city) + '''"})
            return b.title, b.author'''
def getQuery2(title):
    return '''match (:Book {title:"''' + str(title) + '''"})-[:MENTIONS]-(c:City)
            return c.name,c.long,c.latt'''
def getQuery3(author):
    return '''match (b:Book {author:"''' + author + '''"})-[:MENTIONS]-(c:City)
                        return b.title, collect(c)'''
def getQuery3Titles(results):
    titles = set()
    for result in results:
        titles.add(result[0])
        
    return list(titles)

def getQuery3Cities(results):
    cities = set()
    for result in results:
        for city in result[1]:
            cities.add((city['name'],city['long'],city['latt']))
    
    return list(cities)

def getQuery4(long, lat, radius):
    return '''MATCH (city:City)
            WITH point({ x: city.long, y: city.latt, crs: 'cartesian' }) AS p1, point({ x: ''' + long + ''' , y: ''' + lat + ''', crs: 'cartesian' }) AS p2, city
            WHERE distance(p1,p2) < ''' + radius + '''
            WITH city
            MATCH (b:Book)-[:MENTIONS]-(c:City)
            WHERE id(c) = id(city)
            RETURN c.name, collect(b.title)'''

@app.route('/', methods = ['GET'])
def getIndex():
    return render_template('index.html')

@app.route('/', methods = ['POST'])
def postIndex():
    _showMain = False
    _showExtra = False
    neo4jQuery = ''
    _result = ''
    _resultExtra = ''
    _values = []
    selectedQuery = request.form.get('selectedQuery')
    
    if(selectedQuery == '1'):
        _showMain = True
        city = request.form.get('cityName')
        _values.append(city)
        neo4jQuery = getQuery1(city)
        _result = neov(neo4jQuery)

    elif(selectedQuery == '2'):
        _showMain = True
        bookTitle = request.form.get('bookTitle')
        _values.append(bookTitle)
        neo4jQuery = getQuery2(bookTitle)
        _result = neov(neo4jQuery)
        createMap(_result)

    elif(selectedQuery == '3'):
        _showMain = True
        _showExtra = True
        authorName = request.form.get('authorName')
        _values.append(authorName)
        neo4jQuery = getQuery3(authorName)
        preResult = neov(neo4jQuery)
        _result = getQuery3Cities(preResult)
        _resultExtra = getQuery3Titles(preResult)
        createMap(_result)

    elif(selectedQuery == '4'):
        _showMain = True
        longitude = request.form.get('longitude')
        latitude = request.form.get('latitude')
        radius = request.form.get('radius')
        _values.append(longitude)
        _values.append(latitude)
        _values.append(radius)
        neo4jQuery = getQuery4(longitude, latitude, radius)
        _result = neov(neo4jQuery)

    return render_template('index.html', showMain=_showMain, showExtra=_showExtra, query=selectedQuery, result=_result, resultExtra=_resultExtra, values=_values)

if __name__ == '__main__':
    app.run(host ='0.0.0.0', port = 3333, debug = True)