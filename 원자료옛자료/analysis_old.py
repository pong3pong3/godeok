"""
퍙택시 읍.면.동.리의 명칭 및 관할구역에 관한 조례에서
구역이 조정된 토지를 과거 지적도에서 추출하고 최근 지적도와 공간결합
"""
import geopandas as gpd
import pandas as pd
gdf_2021 = gpd.read_file('../중간자료/godeok.gpkg')[['geometry','PNU','SGG_OID']]
gdf = gpd.read_file('godeok_20151118.gpkg').to_crs(gdf_2021.crs)
def make_pnu(string):
    if '-' in string:
        return ''.join(map(lambda x: x.zfill(4), string.split('-')))
    return string.zfill(4)+'0'*4

hgj = '''327, 327-1, 328, 328-1~4, 329, 329-1~5,
 330, 330-1~8, 331, 331-1, 332, 332-1~4, 333, 334, 335, 336,
 337, 338, 339, 340, 341, 129-6~7, 130-8~12, 131-5~8,
 138-11~16, 140-1~2, 141-1~4, 152-3, 153, 153-8~9, 161'''
hgj = hgj.replace(' ','').replace('\n','').split(',')
length = len(hgj)
for i in range(length):
    if '~' not in hgj[i]:
        hgj[i] = make_pnu(hgj[i])
    else:
        body = hgj[i].split('~')
        head, tail = body
        hair, neck = head.split('-')
        hgj[i] = make_pnu(head)
        for j in range(int(neck), int(tail)):
            hgj.append(make_pnu(hair+'-'+str(j+1)))

gdf_2018 = gdf.loc[gdf['A1'].isin(['4122032028'+i for i in (
     '104250020','104250021','104250022','200260001')]+
                                  ['41220320301'+i for i in hgj]),
                   ['A1','geometry']] # 황구지리, 장등리

hgj = '''685, 686, 687, 688, 685-2~32, 686-1~11, 687-1~11, 688-1~7,
 82-1, 82-4~5, 82-7, 83-1, 83-6'''
hgj = hgj.replace(' ','').replace('\n','').split(',')
length = len(hgj)
for i in range(length):
    if '~' not in hgj[i]:
        hgj[i] = make_pnu(hgj[i])
    else:
        body = hgj[i].split('~')
        head, tail = body
        hair, neck = head.split('-')
        hgj[i] = make_pnu(head)
        for j in range(int(neck), int(tail)):
            hgj.append(make_pnu(hair+'-'+str(j+1)))

gdf_2019 = gdf.loc[gdf['A1'].isin(['41220122001'+i for i in hgj]),
                    ['A1','geometry']] # 신대동

dongo = '''79-8~30, 79-32~35, 79-37~49, 79-51~72,
 79-74~75, 79-77~81, 79-84, 79-91~92, 79-98, 79-100~103, 
 79-105~106, 79-108, 79-110~111, 79-113~129, 79-131~132,
 79-135~158, 79-161~199, 79-201~202, 80-1, 81-63, 81-69~71,
 82-43~44, 426-1, 427-1~3'''
dongo = dongo.replace(' ','').replace('\n','').split(',')
length = len(dongo)
for i in range(length):
    if '~' not in dongo[i]:
        dongo[i] = make_pnu(dongo[i])
    else:
        body = dongo[i].split('~')
        head, tail = body
        hair, neck = head.split('-')
        dongo[i] = make_pnu(head)
        for j in range(int(neck), int(tail)):
            dongo.append(make_pnu(hair+'-'+str(j+1)))

gdf_dongo = gdf.loc[gdf['A1'].isin(['41220330271'+i for i in dongo]),
                    ['A1','geometry']] # 동고리
del gdf
'''
import matplotlib.pyplot as plt
tmp = gdf_dongo.copy()
tmp.geometry = tmp.buffer(-.3)
tmp = tmp.sjoin(gdf_2021)
base = tmp.boundary.plot(color='blue')
gdf_2021.loc[gdf_2021['SGG_OID'].isin(tmp['SGG_OID'])].boundary.plot(
    color='red',alpha=.5,ax=base)
plt.show() # 버퍼 검안
tmp = gdf_dongo.overlay(gdf_2021.loc[gdf_2021['PNU'].str.startswith('4122012200')],
                        how='intersection')
tmp['area'] = tmp['geometry'].area
left = tmp.loc[tmp.groupby('A1')['area'].idxmax()]
right = tmp.loc[tmp.loc[~tmp['SGG_OID'].isin(left['SGG_OID'])].\
                groupby('SGG_OID')['area'].idxmax()]
base = left.plot(color='blue')
right.plot(color='red',ax=base,alpha=.5)
gdf_dongo.boundary.plot(color='black',ax=base)
plt.show()
# 다른 현재 신대동 지번과 같은 지번이었던 현재 신대동 지번
# 690-3,7,18,22,25,29,32,35,38,41,44,47,50,53, 691-4, 692-25
'''
def tracker(old, new, timestamp, buf=None):
    if buf: # 두 지적도의 좌표계 어긋남 때문에 버퍼 주어야 제대로 결합가능
        old = old.copy()
        old.geometry = old.geometry.buffer(-buf)
        if old['geometry'].apply(lambda x: x.is_empty).any():
            raise Exception # 버퍼를 너무 심하게 준 경우
        result = old.sjoin(new, how='inner', predicate='intersects')
    if not buf: # 어지간한 버퍼로는 해결되지 않는경우 최대면적법 이용
        result = old.overlay(new, how='intersection')
        result['area'] = result['geometry'].area
        result_left = result.loc[result.groupby('A1')['area'].idxmax()]
        result_right = result.loc[
            result.loc[~result['SGG_OID'].isin(result_left['SGG_OID'])].\
                                  groupby('SGG_OID')['area'].idxmax()]
        result = pd.concat([result_left, result_right])
    result['changed_year'] = str(timestamp)
    result['SGG_OID'] = result['SGG_OID'].astype(str)
    return result[['A1','SGG_OID','changed_year']]

pd.concat([tracker(gdf_2018, gdf_2021, 2018, .2),
           tracker(gdf_2019, gdf_2021, 2019, .3),
           tracker(gdf_dongo,
                   gdf_2021.loc[gdf_2021['PNU'].str.startswith('4122012200')],
                   2019)
           ]).set_index('SGG_OID').to_pickle('../중간자료/boundary.pk')
