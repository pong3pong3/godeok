from flask import Flask, request
import geopandas as gpd
from sqlite3 import connect
import pandas as pd

con = connect('gd.gpkg')
code = pd.read_sql('SELECT * FROM code', con)
gdf = gpd.read_file('gd.gpkg', layer='map')
gdf['법정동코드'] = gdf['land_code'].str[:5]
gdf['대장구분'] = gdf['land_code'].str[5]
gdf = gdf.merge(code, on='법정동코드').drop(columns='법정동코드')
def split_land_code(year):
    tmp = gdf.loc[gdf['year']==year].drop(columns='year')
    tmp['본번'+year] = tmp['land_code'].str[-8:-4]
    tmp['부번'+year] = tmp['land_code'].str[-4:]
    return tmp.drop(columns='land_code').rename(
        columns={'법정동이름': '소재'+year})
gdf_2022 = split_land_code('2022')
gdf_2021 = split_land_code('2021')
gdf_2015 = split_land_code('2015')
gd = pd.read_sql('SELECT * FROM godeok', con)
con.close()
gd = gd.merge(
    gdf_2022, how='left').rename(columns={'geometry': 'geom_2022'}).merge(
        gdf_2021, how='left').rename(columns={'geometry': 'geom_2021'}).merge(
            gdf_2015, how='left').rename(columns={'geometry': 'geom_2015'})
#print(gd[['geom_2022', 'geom_2021', 'geom_2015']].isna().value_counts())
gd = gd.dropna(subset=['geom_2022', 'geom_2021', 'geom_2015'],
               how='all').reset_index(drop=True)
for year in range(2014, 2023):
    year = str(year)
    gd[year] = gd['소재'+year] + gd['대장구분'].apply(
        lambda x: ' ' if x=='1' else ' 산')+ gd['본번'+year].str.lstrip('0')\
        + gd['부번'+year].str.lstrip('0').apply(lambda x: x if not x else '-'+x)
to_numeric = gd.columns.str.startswith('본번')
gd.loc[:, to_numeric] = gd.loc[:, to_numeric].apply(pd.to_numeric)
def draw_map(time, space, kind):
    tmp = gd.loc[(gd['소재'+time]==space)&(gd['대장구분']==kind),
                 ['지목', '면적', '조서구분', '등록전환구분']+
                 [str(i) for i in range(2014, 2023)]+
                 ['geom_2015', 'geom_2021', 'geom_2022', '본번'+time]]
    ambig = tmp['geom_2021'].notna() & tmp['geom_2015'].notna()
    if int(time) > 2018:
        tmp.loc[ambig, 'geom_2015'] = None
    else:
        tmp.loc[ambig, 'geom_2021'] = None
    duplicates = tmp.loc[tmp['geom_2015'].notna(), '2015'
                         ].duplicated(keep='last')
    tmp = tmp.drop(index=duplicates.index[duplicates])
    blank = tmp['geom_2021'].isna()
    tmp.loc[blank, 'geom_2021'] = tmp.loc[blank, 'geom_2015'].values
    blank = tmp['geom_2021'].isna()
    tmp.loc[blank, 'geom_2021'] = tmp.loc[blank, 'geom_2022'].values
    tmp = tmp.drop(columns=['geom_2022', 'geom_2015']).rename(
        columns={'geom_2021': 'geometry'})
    return gpd.GeoDataFrame(tmp).explore(
        column='본번'+time, tooltip=['지목', '면적', '조서구분', '등록전환구분']+\
        [str(i) for i in range(2014, 2023)], popup=time, cmap='brg')._repr_html_()

app = Flask(__name__)
@app.route('/map')
def show_map(): 
    return draw_map(request.args['year'], request.args['zone'], request.args['kind'])
app.run(port=3433)
