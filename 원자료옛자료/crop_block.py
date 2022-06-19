import geopandas as gpd
gdf = gpd.read_file('토지이용계획도_경기_20220216/the_geom.shp',encoding='cp949')
gdf = gdf.loc[gdf['zoneCode']=='41220MX2006001'].drop(
    columns=['zoneCode','zoneName'])
gdf.to_file('고덕_국제화계획지구_및_택지개발지구_(기준고시202111).gpkg', driver='GPKG')
