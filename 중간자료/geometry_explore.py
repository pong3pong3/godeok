import geopandas as gpd
import matplotlib.pyplot as plt
import pandas as pd

# 불연속 지적도
gdf = gpd.read_file('gaori.gpkg')[['geometry']].dissolve()
gdf = gpd.GeoDataFrame(geometry=[i for i in gdf.squeeze()],
                       crs=gdf.crs)
cent = gdf['geometry'].centroid#.to_crs('epsg:4326')
base = gdf.plot()
cent.plot(ax=base, color='red')
plt.show()

# 겹친 토지
gdf = gpd.read_file('gaori.gpkg').to_crs('epsg:4326')
gdf.plot(alpha=.5)

# 겹친 토지 돋보기
gdf = gpd.read_file('gaori.gpkg', layer='ray')
ex1 = gdf.loc[(gdf['2021_소재']=='고덕동')&(gdf['2021_본번']=='1694')&
              (gdf['2021_부번']=='1187')]
ex2 = ex1.overlay(gdf)

ex1 = gdf.loc[(gdf['2021_소재']=='고덕동')&(gdf['2021_본번']=='1346')&
              (gdf['2021_부번']=='0001')]
ex2 = gdf.loc[(gdf['2021_소재']=='고덕동')&(gdf['2021_본번']>='1289')&
              (gdf['2021_본번']<='1290')]
ex3 = gdf.loc[(gdf['2021_소재']=='고덕동')&(gdf['2021_본번']=='1267')&
              (gdf['2021_부번']=='0000')]
base = ex1.plot(alpha=.5,color='blue')
ex2.plot(alpha=.5,ax=base,color='red')
ex3.plot(alpha=.5,ax=base,color='green')
