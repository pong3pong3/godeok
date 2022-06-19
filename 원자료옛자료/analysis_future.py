"""
2022년 4월 지적도와 평택시공고 제2022-549호의 확정토지 일치 확인
"""
import pandas as pd
import geopandas as gpd
from collections import Counter
news = pd.read_excel('../중간자료/220216 평택(송민) 확정토지 지번별 조서.xlsx',
                     header=5, index_col=0,
                     names=['2022_소재','지번','2022_지목','2022_면적',
                            '소유자','용도','구분1','구분2','비고']).iloc[:-1]
news = news.drop(columns=['2022_지목','2022_면적','소유자','용도',
                          '구분1','구분2','비고'])
news = '41220128001' + news['지번'].astype(str).str.split('-').apply(
    lambda x: x[0]).str.zfill(4) + news['지번'].astype(str).str.split('-').apply(
    lambda x: x[1].zfill(4) if len(x)==2 else '0000')
news.iloc[-15:] = news.iloc[-15:].str[:5] + '33025' + news.iloc[-15:].str[10:]
news.index = news.str[5:-4]
news.index.name = '본번'
gdf = gpd.read_file('LSMD_CONT_LDREG_경기_평택시/LSMD_CONT_LDREG_41220.shp', encoding='cp949')
gdf = gdf.loc[gdf['pnu'].str.startswith('41220128001')|
              gdf['pnu'].str.startswith('41220330251'), 'pnu'].sort_values()
assert news.isin(gdf).all()
gdf.index = gdf.str[5:-4]
gdf.index.name = '본번'
news = news.loc[~news.index.duplicated(keep='last')]
gdf = gdf.loc[~gdf.index.duplicated(keep='last')]
df = pd.merge(news,gdf,left_index=True,right_index=True)
assert (df['지번']==df['pnu']).all()
