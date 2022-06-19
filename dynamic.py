from flask import Flask, request
import geopandas as gpd

gdf = gpd.read_file('gaori.gpkg').dropna(subset=['geometry'])
def draw_map(space, time, space_2=''):
    tmp = gdf.loc[gdf[time+'_소재'].isin([space,space_2]),
                  [time+'_본번',time+'_부번','대장구분','geometry']]
    tmp[time+'_본번'] = tmp[time+'_본번'].astype(int)
    return tmp.explore(column=time+'_본번',
                       tooltip=[time+'_본번',
                                time+'_부번',
                                '대장구분'])._repr_html_()

app = Flask(__name__)

@app.route('/map')
def show_map(): 
    return draw_map(request.args['town'],
                    request.args['year'],
                    request.args['town2'],)

if __name__=='__main__':
    app.run(port=3433)
