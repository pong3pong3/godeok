"""
평택시 고시 제 2017-229호의 토지조서를 정제하여 신규토지의 최소부번값 추출
"""
import pandas as pd
import numpy as np
import geopandas as gpd
df = pd.read_excel('중로1-80.xlsx',
                   header=1, dtype=str).iloc[1:122,:5]
df.columns = ['연번','소재','기정','변경','지목']
df = df.loc[df['소재']!='신리'].replace(
    ' ', np.nan).dropna(how='all')
df['연번'] = df['연번'].fillna(method='ffill').astype(int)
df = df.set_index('연번')
assert ~df['변경'].str.startswith('산').any()
def make_pnu(string):
    if '-' in string:
        return ''.join(map(lambda x: x.strip().zfill(4), string.split('-')))
    return string.strip().zfill(4)+'0'*4
old = '41220330281' + df.loc[df['기정'].notna(),'기정'].apply(make_pnu)
old.iloc[-1] = old.iloc[-1].replace('4122033028','4122033026')
new = '41220330281' + df.loc[df['변경'].notna(),'변경'].apply(make_pnu)
new.iloc[-1] = new.iloc[-1].replace('4122033028','4122033026')
gdf = gpd.read_file('godeok.gpkg')['PNU']
gdf = gdf.loc[(gdf.str.startswith('4122033026'))|
              (gdf.str.startswith('4122033028'))]
assert ~bool(set(old)-set(gdf))
assert ~bool(set(new)-set(gdf))
df = pd.concat([old,new], axis=1)
assert (df['변경'].str[11:15]==df['기정'].str[11:15]).all()
assert (df['변경']>=df['기정']).all()
df['id'] = df['변경'].str[9:15]
df = df.loc[df['변경']!=df['기정']].groupby('id')[['변경']].min()
df[['2017_소재','대장구분','2017_본번','최소_부번']] =\
    df['변경'].str.extract('412203302(\d)(\d)(\d{4,4})(\d{4,4})')
df['2017_소재'] = df['2017_소재'].replace('6','고덕면 궁리').replace('8','고덕면 방축리')
df.reset_index(drop=True).drop(columns=['변경']).to_pickle('중로1-80.pk')
