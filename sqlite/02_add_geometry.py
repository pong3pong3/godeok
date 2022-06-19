"""
노골적인 중첩을 제거한 지적도형 및 법정동리 코드를 추가하여 DB 새로 생성
"""
import pandas as pd
import geopandas as gpd
from sqlite3 import connect
village_dictionary = pd.read_csv('../중간자료/법정동코드.tsv', sep='\t',
                                 dtype=str).set_index('법정동이름').squeeze()
con = connect('godeok.db')
sql = 'SELECT DISTINCT 대장구분, 소재{0}, 본번{0}, 부번{0} FROM godeok'
result = gpd.GeoDataFrame()
for year in (2021, 2015, 2022):
    if year==2021:  # 고덕동 1727은 고덕동 1727-1로 분할됐었는데 2021년 지적도엔 반영 안됨
        gdf = gpd.read_file('../중간자료/godeok.gpkg')[['PNU','geometry']]
        gdf = gdf.loc[gdf['PNU']!='4122012800117270000']
    elif year==2015:
        gdf = gpd.read_file('../원자료옛자료/godeok_20151118.gpkg')[
            ['A1','geometry']].to_crs(gdf.crs)
    else:
        gdf = gpd.read_file('../원자료옛자료/LSMD_CONT_LDREG_경기_평택시/LSMD_CONT_LDREG_41220.shp')[
            ['pnu','geometry']].set_crs(gdf.crs)
    gdf.columns = ['land_code', 'geometry']
    gdf['year'] = str(year)
    gdf['land_code'] = gdf['land_code'].str[5:]
    if year==2015:
        db = pd.read_sql(sql.format(year) + ' WHERE 소재2021 IS NULL', con).merge(
            village_dictionary, left_on='소재{0}'.format(year), right_index=True)
    else:
        db = pd.read_sql(sql.format(year), con).merge(
            village_dictionary, left_on='소재{0}'.format(year), right_index=True)
    result = pd.concat([result,
                        gdf.loc[gdf['land_code'].isin(
                            db['법정동코드']+db['대장구분']+
                            db['본번{0}'.format(year)]+
                            db['부번{0}'.format(year)])]
                        ])
db = pd.read_sql('SELECT * FROM godeok', con)
con.close()
result = result.loc[~result['land_code'].duplicated(keep='first')] # 최신 지적도형만

def make_pnu(address):
    address = address.split(' ')
    if len(address)==2:
        village_name, land_code = address
    elif len(address)==3:
        village_name, land_code = ' '.join(address[:-1]), address[-1]
    return ''.join([
        village_dictionary[village_name],
        '2' if land_code[0]=='산' else '1',
        land_code.split('-')[0].lstrip('산').zfill(4),
        land_code.split('-')[1].zfill(4) if '-' in land_code else '0000'])

with open('../중간자료/overlap.txt', 'r', encoding='utf-8') as file:
    overlap_list = list(
        map(lambda x: x.split('\n'), file.read().split('\n\n'))
        )[:-2]

for element in overlap_list:
    target = result['land_code']==make_pnu(element[0])
    overlaps = list(map(make_pnu, element[1:]))
    if overlaps:
        result.loc[target] = gpd.overlay(
            result.loc[target], result.loc[result['land_code'].isin(overlaps)],
            how='difference').values
    else:
        result.loc[target] = gpd.overlay(
            result.loc[target],
            result.loc[(result['year'] == result.loc[target, 'year'].squeeze())&
                       ~target],
            how='difference').values

result[['land_code', 'year', 'geometry']].sort_values(by='land_code').to_file(
    'gd.gpkg', layer='map', driver='GPKG')
con = connect('gd.gpkg')
village_dictionary.drop(index=['신대동', '서탄면 황구지리', '서탄면 장등리',
                               '고덕면 동고리', '고덕면 동청리', '고덕면 문곡리']
                        ).sort_values().to_sql('code', con)
db.to_sql('godeok', con, index=False)
con.close()
