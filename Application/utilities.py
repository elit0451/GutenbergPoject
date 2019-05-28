import folium

def createMap(locations):
    m = folium.Map(
        location=[30.816676, -32.215901],
        zoom_start=2,
        min_zoom=2,
        min_lon=-45,
        max_lon=-35,
        max_bounds=True
    )

    if(len(locations) > 0):
        for location in locations:
            tooltip = location[0]
            folium.Marker([location[2], location[1]], popup='<i><b>latitude</b>: ' + str(location[1]) + ', <b>longitude</b>: ' + str(location[2]) + '</i>', tooltip=tooltip).add_to(m)

    return m._repr_html_()