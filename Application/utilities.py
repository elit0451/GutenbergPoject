import folium

def createMap(locations):
    if(len(locations) > 0):
        m = folium.Map(
            location=[locations[0][2], locations[0][1]],
            zoom_start=2
        )

        tooltip = 'Click me!'

        for location in locations:
            folium.Marker([location[2], location[1]], popup='<i>' + location[0] + '</i>', tooltip=tooltip).add_to(m)

    m.save('templates/map.html')