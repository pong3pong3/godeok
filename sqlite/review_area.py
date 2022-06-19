"""
장부상 면적과 지적도상 면적 비교
"""
import geopandas as gpd
import pandas as pd
from sqlite3 import connect
import matplotlib.pyplot as plt
import numpy as np
gdf = gpd.read_file('gd.gpkg', layer='map')
gdf['area'] = gdf['geometry'].area
con = connect('gd.gpkg')
df = pd.read_sql('SELECT * FROM godeok', con)
code_table = pd.read_sql('SELECT * FROM code', con)
con.close()
df_2022 = df.loc[df['소재2022'].notna(),
                 ['대장구분', '소재2022', '본번2022', '부번2022', '면적']
                 ].merge(code_table.rename(columns={'법정동이름': '소재2022'}),
                         on='소재2022')
df_2022['land_code'] = df_2022['법정동코드'] + df_2022['대장구분'] +\
                       df_2022['본번2022'] + df_2022['부번2022']
df_2021 = df.loc[df['소재2021'].notna()&df['소재2022'].isna(),
                 ['대장구분', '소재2021', '본번2021', '부번2021', '면적']
                 ].merge(code_table.rename(columns={'법정동이름': '소재2021'}),
                         on='소재2021')
df_2021['land_code'] = df_2021['법정동코드'] + df_2021['대장구분'] +\
                       df_2021['본번2021'] + df_2021['부번2021']
df_2015 = df.loc[df['소재2021'].isna()&df['소재2015'].notna(),
                 ['대장구분', '소재2015', '본번2015', '부번2015']
                 ]
assert len(df_2022)+len(df_2021)+len(df_2015) == len(df)-1 # 서정동393-16
df_2015 = df[['대장구분', '소재2015', '본번2015', '부번2015', '면적']].merge(
    df_2015.drop_duplicates(),
    on=['대장구분', '소재2015', '본번2015', '부번2015']).merge(
        code_table.rename(columns={'법정동이름': '소재2015'}), on='소재2015')
df_2015['land_code'] = df_2015['법정동코드'] + df_2015['대장구분'] +\
                       df_2015['본번2015'] + df_2015['부번2015']
df_2015 = df_2015.groupby('land_code')['면적'].sum().reset_index()
df = pd.concat([df_2022[['land_code', '면적']],
                df_2021[['land_code', '면적']],
                df_2015[['land_code', '면적']]
                ]).drop_duplicates(subset=['land_code'], keep='first')
df = gdf.merge(df, on='land_code').set_index('land_code')
df['ratio'] = df['area']/df['면적']
df['diff'] = abs(df['area'] - df['면적'])
df['log_ratio'] = np.log10(df['ratio'])
df = df.sort_values(by='ratio')
plt.plot(df['log_ratio'])
plt.show()
