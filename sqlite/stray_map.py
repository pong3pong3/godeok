from sqlite3 import connect
import pandas as pd
import geopandas as gpd
con = connect('gd.gpkg')
df = pd.read_sql('''
SELECT 조서구분, 지목, 대장구분,
소재2018, 본번2018, 부번2018, 소재2017, 본번2017, 부번2017,
법정동코드 || 대장구분 || 본번2021 || 부번2021 AS land_code
FROM godeok LEFT JOIN code ON 소재2021=법정동이름
WHERE 소재2018 IS NOT NULL
AND (조서구분 <> '1' OR 조서구분 IS NULL)
UNION
SELECT 조서구분, 지목, 대장구분,
소재2018, 본번2018, 부번2018, 소재2017, 본번2017, 부번2017,
법정동코드 || 대장구분 || 본번2015 || 부번2015 AS land_code
FROM godeok LEFT JOIN code ON 소재2015=법정동이름
WHERE 소재2018 IS NOT NULL AND 조서구분 = '1'
''', con).set_index(['소재2018', '대장구분', '본번2018'])
con.close()
df = df.loc[df.index[df['소재2017'].isna()].unique()].reset_index()
df = gpd.read_file('gd.gpkg', layer='map')[['land_code', 'geometry']].merge(
    df, on='land_code', how='inner')
df['신규'] = df['소재2017'].isna().astype(str)
df.explore(column='신규',
           tooltip=['조서구분', '지목', '대장구분', '소재2018',
                    '본번2018', '부번2018', '소재2017', '본번2017', '부번2017'
                    ]).save('stray_map.html')
