from flask import Flask, request
import geopandas as gpd

gdf = gpd.read_file('gd.gpkg', layer='map')
def draw_map(time):
    tmp = gdf.loc[gdf['year']==time,
                  ['land_code','geometry']]
    tmp['village'] = tmp['land_code'].str[:5]
    return tmp.explore(column='village',
                       tooltip=['land_code'])._repr_html_()

app = Flask(__name__)

@app.route('/map')
def show_map(): 
    return draw_map(request.args['year'])

if __name__=='__main__':
    app.run(port=3433)
