"""
고덕 국제화계획지구 및 택지개발지구에 해당하는 지번만 추출해서 정리
"""
import pandas as pd
import geopandas as gpd
import sqlite3
from shapely.geometry import Polygon
gdf = gpd.read_file('../gaori.gpkg')
gdf = gdf.loc[gdf['2021_소재'].isin(['고덕동', '고덕면 여염리'])|
              gdf['등록'].isin(['0', '1', '6'])|
              gdf['말소'].isin(['0', '1', '6'])|
              gdf.index.isin(gpd.GeoDataFrame(
                  geometry=gpd.read_file('../중간자료/고덕_국제화계획지구_및_택지개발지구_(기준고시202111).gpkg')
                  [['geometry']].dissolve().to_crs(gdf.crs)['geometry'].apply(
                      lambda x: Polygon(x.exterior)).buffer(-1)).sjoin(
                          gdf.loc[gdf['2021_소재']=='고덕면 해창리'])['index_right'])
              ].reset_index(drop=True)
gdf['조서구분'] = gdf['등록'].fillna(gdf['말소']).replace('6','2')
target = gdf['2021_소재'].isin(['고덕면 여염리', '고덕면 해창리'])
# 지목이나 면적이 누락될 가능성이 높은 경우 비상용으로 채워주기
gdf.loc[target, '2015_지목'] = gdf.loc[target, 'JIBUN'].str[-1]
gdf.loc[(gdf['대장구분']=='1')&(gdf['2017_소재']=='서정동')&
        (gdf['2017_본번']=='0381')&(gdf['2017_부번']=='0028'),
        '2015_지목'] = '답'  # 국토교통부고시 제2019-298호에서 확인
gdf.loc[target, '2015_면적'] = gdf.loc[target, 'geometry'].area
gdf_fixed = gdf.loc[:, gdf.columns.str.endswith('구분')|
                    gdf.columns.str.endswith('소재')|gdf.columns.str.endswith('번')
                    ].rename(columns={i: ''.join(reversed(i.split('_')))
                                      for i in gdf.columns
                                      if i[-1]=='재' or i[-1]=='번'})
gdf_area = gdf.loc[:, gdf.columns.str.endswith('면적')].bfill(axis=1).iloc[
    :, :1].rename(columns={'2022_면적':'면적'})
gdf_purpose = gdf.loc[:, gdf.columns.str.endswith('지목')].bfill(axis=1).iloc[
    :, :1].rename(columns={'2022_지목':'지목'}).replace({
        '전':'밭', '답':'논', '대':'대지', '구':'구거', '주':'주유소용지',
        '도':'도로', '임':'임야', '잡':'잡종지', '공':'공원', '차':'주차장',
        '장':'공장용지', '철':'철도용지', '과':'과수원', '목':'목장용지',
        '창':'창고용지', '묘':'묘지', '유':'유지', '천':'하천', '제':'제방'})
df = pd.concat([gdf_fixed, gdf_purpose, gdf_area], axis=1).dropna(
    subset='지목').reset_index(drop=True)  # 고덕동 547-9처럼 지적도 주소가 틀린 경우 제거
df.sort_values(by=df.columns.tolist()).to_sql('godeok',
                                              sqlite3.connect('godeok.db'),
                                              if_exists='replace',
                                              index=False)

