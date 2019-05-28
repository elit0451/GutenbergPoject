#!/usr/bin/python3

import mongoImporter
from neo4jImporter import neov
from utilities import createMap

from flask import Flask,render_template, request,jsonify,Response

app = Flask(__name__)

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
    selectedDB = request.form.get('selectedDB')
    
    if(selectedQuery == '1'):
        _showMain = True
        city = request.form.get('cityName')
        _values.append(city)
        if(selectedDB == 'neo4j'):
            neo4jQuery = neoQuery1(city)
            _result = neov(neo4jQuery)
        elif(selectedDB == 'mongo'):    
            print('Mongo')

    elif(selectedQuery == '2'):
        _showMain = True
        bookTitle = request.form.get('bookTitle')
        _values.append(bookTitle)
        neo4jQuery = neoQuery2(bookTitle)
        _result = neov(neo4jQuery)
        createMap(_result)

    elif(selectedQuery == '3'):
        _showMain = True
        _showExtra = True
        authorName = request.form.get('authorName')
        _values.append(authorName)
        neo4jQuery = neoQuery3(authorName)
        preResult = neov(neo4jQuery)
        _result = neoQuery3Cities(preResult)
        _resultExtra = neoQuery3Titles(preResult)
        createMap(_result)

    elif(selectedQuery == '4'):
        _showMain = True
        longitude = request.form.get('longitude')
        latitude = request.form.get('latitude')
        radius = request.form.get('radius')
        _values.append(longitude)
        _values.append(latitude)
        _values.append(radius)
        neo4jQuery = neoQuery4(longitude, latitude, radius)
        _result = neov(neo4jQuery)

    return render_template('index.html', showMain=_showMain, showExtra=_showExtra, query=selectedQuery, result=_result, resultExtra=_resultExtra, values=_values)

if __name__ == '__main__':
    app.run(host ='0.0.0.0', port = 3333, debug = True)