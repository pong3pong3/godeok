import geopandas as gpd

# 1단계: 노골적으로 중첩된 필지들의 중첩을 제거
import pandas as pd
village_dictionary = pd.read_csv('../중간자료/법정동코드.tsv', sep='\t',
                                 dtype=str).set_index('법정동이름').squeeze()
with open('../중간자료/overlap.txt', 'r', encoding='utf-8') as file:
    overlap_list = map(lambda x: x.split('\n'), file.read().split('\n\n'))
gdf = gpd.read_file('ray.gpkg', layer='ray')
def search_engine(address):
    address = address.split(' ')
    if len(address)==2:
        village_name, land_code = address
    elif len(address)==3:
        village_name, land_code = ' '.join(address[:-1]), address[-1]
    return {'village_code_2021':village_dictionary[village_name],
            'ledger_code':'2' if land_code[0]=='산' else '1',
            'land_main_code_2021':land_code.split('-')[0].lstrip('산').zfill(4),
            'land_sub_code_2021':land_code.split('-')[1].zfill(4) \
            if '-' in land_code else '0000'}
for element in overlap_list:
    subtractee = search_engine(element[0])
    left = '&'.join(["(gdf['{0}']=='{1}')".format(
        list(subtractee.keys())[i], list(subtractee.values())[i])
                     for i in range(len(subtractee))])
    if len(element)==1:
        right = left.replace("sub_code_2021']=","sub_code_2021']!")
    else:
        right = []
        for i in range(1,len(element)):
            subtractor = search_engine(element[i])
            if element[i][-1]=='-':
                right.append('&'.join(["(gdf['{0}']=='{1}')".format(
                    list(subtractor.keys())[i], list(subtractor.values())[i])
                                        for i in range(len(subtractor)-1)]))
            else:
                right.append('&'.join(["(gdf['{0}']=='{1}')".format(
                    list(subtractor.keys())[i], list(subtractor.values())[i])
                                        for i in range(len(subtractor))]))
        right = '('+')|('.join(right)+')'
    gdf.loc[eval(left)] = gpd.overlay(gdf.loc[eval(left)],
                                      gdf.loc[eval(right)], how='difference').values
gdf.to_file('ray.gpkg', layer='ray', driver='GPKG')

# 2단계: 이제 rayborhood.sql 돌리자 (행정구역 변천유형별로 그룹한 rayborhood 레이어 생성)
# 3단계: rayborhood 레이어의 폴리곤 가운데 빈 구멍은 제거
from shapely.geometry import Polygon, MultiPolygon
gdf = gpd.read_file('ray.gpkg', layer='rayborhood')
for i in range(len(gdf)):
    print(i)
    geom = gdf['geometry'].loc[i]
    complement = gdf[['geometry']].drop(index=i).dissolve().squeeze()
    if type(geom)==Polygon:
        proper_interiors = []
        for interior in geom.interiors:
            if Polygon(interior).intersects(complement):
                proper_interiors.append([
                    coord for coord in interior.coords])
        gdf['geometry'].loc[i] = Polygon(geom.exterior, proper_interiors)
    elif type(geom)==MultiPolygon:
        geoms = []
        for geom in geom:
            proper_interiors = []
            for interior in geom.interiors:
                if Polygon(interior).intersects(complement):
                    proper_interiors.append([
                        coord for coord in interior.coords])
            geoms.append(Polygon(geom.exterior, proper_interiors))
        gdf['geometry'].loc[i] = MultiPolygon(geoms)
# 멀티폴리곤을 폴리곤으로 분리한 다음 다시 합쳐서 채워진 구멍 안에 이미 폴리곤이 있던 경우 이를 제거
gdf = gdf.explode(index_parts=False).reset_index(drop=False).dissolve('index').\
      reset_index(drop=True) # 마지막 reset은 gpkg 저장 시 fid 컬럼 외에 index컬럼이 중복으로 생기는 걸 방지
gdf.to_file('ray.gpkg', layer='rayborhood', driver='GPKG')

# 4단계: 인접한 폴리곤끼리는 같은 색깔이 배정받지 않도록 색깔 설정
gdf = gpd.read_file('ray.gpkg', layer='rayborhood')
gdf['neighbors'] = [set() for i in range(len(gdf))]
for i in range(len(gdf)):
    print(i)
    neighbor = gdf[['geometry']].drop(index=i).sjoin(
        gdf[['geometry']].iloc[i:i+1], predicate='intersects').index
    gdf.loc[neighbor, 'neighbors'].apply(lambda x: x.add(i))
gdf['color_code'] = None
for i in range(len(gdf)):
    color = 0
    bans = gdf.loc[gdf.loc[i, 'neighbors'], 'color_code'].dropna().unique()
    for ban in sorted(bans):
        if color==ban:
            color+=1
            continue
        break
    gdf.loc[i, 'color_code'] = color
gdf.drop(columns='neighbors').to_file('ray.gpkg', layer='rayborhood', driver='GPKG')

# 5단계: 10가지 기본 색깔 가운데 아직 안 쓰인 3가지를 여러 번 쓰이는 색깔의 절반에 적용
import matplotlib.pyplot as plt
gdf = gpd.read_file('ray.gpkg', layer='rayborhood')
gdf['color_code'] = gdf['color_code'].astype(int)
for i in range(3):
    couple = gdf.loc[gdf['color_code']==i].index
    gdf.loc[couple[1::2], 'color_code']+=7
gdf['color_code'] = gdf['color_code'].astype(str)
gdf.explore(column='color_code',
	    tooltip=['village_name_'+str(i) for i in range(2016,2023)],
	    legend=False,
	    style_kwds={'color':'black'}).save('rayborhood.html')
ax = gdf.plot(column='color_code')
ax.set_axis_off()
plt.show()
