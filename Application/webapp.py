#!/usr/bin/python3
from utilities import createMap
from flask import Flask,render_template, request,jsonify,Response
from queryComposer import executeQuery

app = Flask(__name__)

@app.route('/', methods = ['GET'])
def getIndex():
    return render_template('index.html')

@app.route('/', methods = ['POST'])
def postIndex():
    _showMain = False
    _showExtra = False
    _createMap = False
    _values = []
    
    selectedQuery = request.form.get('selectedQuery')
    selectedDB = request.form.get('selectedDB')
    
    if(selectedQuery == '1'):
        _showMain = True
        city = request.form.get('cityName')
        _values.append(city)

    elif(selectedQuery == '2'):
        _showMain = True
        bookTitle = request.form.get('bookTitle')
        _values.append(bookTitle)
        _createMap = True

    elif(selectedQuery == '3'):
        _showMain = True
        _showExtra = True
        authorName = request.form.get('authorName')
        _values.append(authorName)
        _createMap = True

    elif(selectedQuery == '4'):
        _showMain = True
        longitude = request.form.get('longitude')
        latitude = request.form.get('latitude')
        radius = request.form.get('radius')
        _values.append(longitude)
        _values.append(latitude)
        _values.append(radius)
    
    
    _result,_resultExtra = executeQuery(selectedDB, selectedQuery, _values)

    if(_createMap):
        createMap(_result)

    return render_template('index.html', showMain=_showMain, showExtra=_showExtra, query=selectedQuery, result=_result, resultExtra=_resultExtra, values=_values)

if __name__ == '__main__':
    app.run(host ='0.0.0.0', port = 3333, debug = True)