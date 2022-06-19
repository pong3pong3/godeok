import geopandas as gpd
gdf = gpd.read_file('경기도_연속지적도형정보_20151224/경기도_연속지적도형정보_20151224.shp')
# 고덕면, 서탄면 황구지리, 서탄면 장등리, 신대동, 서정동, 장당동
gdf = gdf.loc[gdf['A2'].str.startswith('41220330')|gdf['A2'].isin(
    ['4122032028','4122032030','4122012200','4122010100','4122010200']),
              ['A0','A1','A5','geometry']]
# A0: SGG_OID(INT), A1: 필지고유번호, A5: 지번-지목
gdf.geometry = gdf.geometry.translate(xoff=257, yoff=.1)
#gdf.loc[(gdf.geometry.centroid.x>300000)&(gdf.geometry.centroid.y>400000)]#오류
gdf.to_file('godeok_20151118.gpkg')
