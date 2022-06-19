"""
2015년 지적도에는 있는데 미래로부터 거슬러올라올 때에는 안보이는 지적도형
및 여염리 등록전환으로 사라진 지적도형과 등록전환구분을 추가
"""
from sqlite3 import connect
import pandas as pd
import geopandas as gpd
gdf = gpd.read_file('../원자료옛자료/godeok_20151118.gpkg'
                    ).rename(columns={'A1':'land_code'}
                             ).set_index('land_code').drop(columns=['A0','A5'])
gdf.index = gdf.index.str[5:]
yy_past_count = len(gdf.index[gdf.index.str.startswith('33029')])
yy_history = pd.read_csv('여염리_등록전환.csv', dtype=str, encoding='cp949')
yy_convert = ('33029' + yy_history.loc[
    yy_history['토지이동사유']=='번으로 등록전환되어 말소', '고유번호']).to_list()
gdf = gdf.loc[yy_convert].to_crs('epsg:5174').reset_index()
gdf['year'] = '2015'
gdf = pd.concat([gpd.read_file('gd.gpkg', layer='map'),
                 gdf]).sort_values(by='land_code').reset_index(drop=True)
gdf[['land_code', 'year', 'geometry']].to_file(
    'gd.gpkg', layer='map', driver='GPKG')

df = pd.read_csv('여염리_등록전환.csv', encoding='cp949', dtype=str).set_index(
    '토지이동이력순번')
df = df.loc[df['토지이동사유']=='번으로 등록전환되어 말소',
            ['고유번호', '지목', '토지면적']]
con = connect('gd.gpkg')
cur = con.cursor()
cur.execute('ALTER TABLE godeok ADD COLUMN 등록전환구분 TEXT')
for order_id in df.index:
    main_id = df.loc[order_id, '고유번호'][1:5]
    sub_id = df.loc[order_id, '고유번호'][-4:]
    purpose = df.loc[order_id, '지목']
    if purpose == '대':
        purpose += '지'
    area = df.loc[order_id, '토지면적']
    cur.execute(f"""INSERT INTO godeok(대장구분, 소재2014, 본번2014, 부번2014,
소재2015, 본번2015, 부번2015, 등록전환구분, 지목, 면적) VALUES
('2', '고덕면 여염리', '{main_id}', '{sub_id}', '고덕면 여염리', '{main_id}', '{sub_id}',
'{order_id}', '{purpose}', {area})""")

dictionary = {'1280507': [('0037', '0001')],
              '1281859': [('0037', '0002'), ('0037', '0003'), ('0037', '0006')],
              '1295661': [('0039', '0030'), ('0039', '0026')],
              '1432381': [('0039', '0034'), ('0039', '0035'), ('0039', '0036')],
              '1432882': [('0037', '0004'), ('0037', '0007'), ('0037', '0008')],
              '1432884': [('0037', '0005'), ('0037', '0009')]}
for order_id in dictionary.keys():
    for land_id in dictionary[order_id]:
        main_id, sub_id = land_id
        cur.execute(f"""UPDATE godeok SET 등록전환구분='{order_id}'
WHERE 소재2016='고덕면 여염리' AND 대장구분='1'
AND 본번2016='{main_id}' AND 부번2016='{sub_id}'""")

# before_20151118
cur.execute("""
INSERT INTO godeok (대장구분, 지목, 면적,
소재2015, 본번2015, 부번2015, 소재2014, 본번2014, 부번2014)
VALUES ('1', '도로', 500.848874,
'고덕면 여염리', '0435', '0006', '고덕면 여염리', '0435', '0006'),
('1', '도로', 22.254082,
'고덕면 궁리', '0325', '0004', '고덕면 궁리', '0325', '0004'),
('1', '제방', 37.969655,
'고덕면 두릉리', '0632', '0002', '고덕면 두릉리', '0632', '0002')
""")
con.commit()

# before_20151118 목록에는 여염리 자투리땅을 고려하지 않았었으나
# 나중에 확인해보니 자투리땅에는 등록전환을 제외하면 다행히도 이런 경우가 없었음
assert yy_past_count == len(pd.read_sql("""
SELECT DISTINCT 법정동코드 || 대장구분 || 본번2015 || 부번2015 FROM godeok
INNER JOIN code ON 소재2015=법정동이름 WHERE 소재2015='고덕면 여염리'""",
                                       con))      
con.close()
