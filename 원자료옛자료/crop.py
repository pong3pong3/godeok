"""
연속지적도 가운데 평택시 고덕면과 고덕동 및 서정동 월경지를 추출
"""
import geopandas as gpd
gdf = gpd.read_file('LSMD_CONT_LDREG_경기/LSMD_CONT_LDREG_41_202112.shp',
                    encoding='cp949')
gdf = gdf[gdf['PNU'].str.startswith('41220')].\
          drop(columns='COL_ADM_SE')
gdf = gdf[gdf['PNU'].str.startswith('41220330')|
          gdf['PNU'].str.startswith('41220128')|
          gdf['PNU'].str.startswith('412201010010607')|
          gdf['PNU'].str.startswith('412201010020106')|
          ((gdf['PNU']>'4122012200106840000')&
           (gdf['PNU']<'4122012200107130000'))]
gdf.crs = 'epsg:5174'
gdf.to_file('godeok.gpkg', driver='GPKG')
