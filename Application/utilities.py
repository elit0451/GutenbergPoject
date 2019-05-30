import folium
import os

dataImported = False

def createMap(locations):
    m = folium.Map(
        location=[30.816676, -32.215901],
        zoom_start=2,
        min_zoom=2,
        min_lon=-180,
        max_lon=180,
        max_bounds=True
    )

    if(len(locations) > 0):
        for location in locations:
            tooltip = location[0]
            folium.Marker([location[2], location[1]], popup='<i><b>latitude</b>: ' + str(location[1]) + ', <b>longitude</b>: ' + str(location[2]) + '</i>', tooltip=tooltip).add_to(m)

    return m._repr_html_()


def getImportDetails():
    booksDir = '../Resources/Books'
    citiesFile = '../Resources/cities5000.csv'
    bookCount = len(os.listdir(booksDir))
    cityCount = num_lines = sum(1 for line in open(citiesFile, encoding='utf-8', errors='replace'))

    return (bookCount, cityCount)


class Importer:
    __instance = None
    @staticmethod 
    def getInstance():
        if Importer.__instance == None:
            Importer()
        return Importer.__instance
    def __init__(self):
        self.totalBooks = 0
        self.totalCities = 0
        self.currentBookParseCount = 0
        self.currentCityCountNeo = 0
        self.currentBookCountNeo = 0
        self.currentCityCountMongo = 0
        self.currentBookCountMongo = 0
        self.imported = False
        if Importer.__instance != None:
            raise Exception("This class is a singleton!")
        else:
            Importer.__instance = self
        
    
    
    def getImportDetails(self):
        if(self.totalBooks == 0 or self.totalCities == 0):
            self.totalBooks,self.totalCities = getImportDetails()

        return self.totalBooks, self.totalCities, self.currentBookParseCount, self.currentBookCountMongo, self.currentCityCountMongo, self.currentBookCountNeo, self.currentCityCountNeo

    def updateProgress(self,database,book,count):
        if(database == 'neo'):
            if(book):
                self.currentBookCountNeo += count
            else:
                self.currentCityCountNeo += self.totalCities
        elif(database == 'mongo'):
            if(book):
                self.currentBookCountMongo += count
            else:
                self.currentCityCountMongo += count
        else:
            self.currentBookParseCount += count
        

        if(self.currentBookCountNeo >= self.totalBooks and self.currentBookCountMongo >= self.totalBooks and self.currentCityCountNeo >= self.totalCities and self.currentCityCountMongo >= self.totalCities and self.currentBookParseCount >= self.totalBooks):
            self.imported = True

    def getImportedState(self):
        return self.imported
