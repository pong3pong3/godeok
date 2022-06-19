"""
만들어진 gaori.gpkg에 2015년11월18일 기준 지적도를 겹쳐서
과거에 없었는데 과거에도 있는 것으로 오인된 지번을 추출하여
그 내용을 다시 godeok.py에 반영
"""
import geopandas as gpd
import pandas as pd
from shapely.geometry import Polygon

# 남쪽도로 신규토지(이거 보고 중로 1-80.pk를 만들게 됨, 이젠 deprecated)
# new = gpd.read_file('godeok.gpkg').set_index('PNU')
# new = new.loc[~new.index.str.startswith('4122012800')]
# old = gpd.read_file('../원자료옛자료/godeok_20151118.gpkg').set_index('A1')
# new.loc[new.index.intersection(old.index)].plot()
# new.loc[new.index.difference(old.index)].explore().save('south_road.html')

# 2015년 이전으로, 남쪽도로에서 고덕 전역으로 확장
new = gpd.read_file('gaori.gpkg')
new = new.loc[new['2016_소재'].notna(), ['대장구분','말소','등록','geometry','SGG_OID']+[
    str(i)+j for i in range(2016,2022) for j in ('_소재','_본번','_부번')]
              ].merge(pd.read_csv('법정동코드.tsv',
                                  sep='\t', dtype=str).rename(
                  columns={'법정동이름':'2016_소재'}),
                      how='left', on=['2016_소재'])
new.index = new['법정동코드'] + new['대장구분'] + new['2016_본번'] + new['2016_부번']
new = new.sort_index()
old = gpd.read_file('../원자료옛자료/godeok_20151118.gpkg')
old.index = old['A1'].str[5:]
old['A1'] = old['A1'].str[5:10]
old = old.sort_index()

# 번외: 고덕신도시 기준 2015년에는 있었는데 미래로부터 조상을 찾을 때 못 찾은 경우
try:
    lost_old = old.sjoin(gpd.GeoDataFrame(
        geometry=gpd.read_file('gaori.gpkg', layer='block')[['geometry']].\
        dissolve().to_crs(old.crs)['geometry'].apply(
            lambda x: Polygon(x.exterior)).buffer(-1))).drop(columns=['index_right'])
    lost_old.loc[~lost_old.index.isin(new.index)].reset_index(drop=True).explore(
        color='blue').save('before_20151118.html')
except ValueError:
    pass

new = new.loc[new.index.difference(old.index)].drop(index=['33026104640000'])
#print(new.loc[new.index.str.endswith('0000')]) # 당현리589
#print(old.loc[old.index.str.startswith('330261')]) # 궁리464는 실수로 빠진 듯
ledger_and_land_main_code = new.index.str[:-4].unique().copy()
for i in ledger_and_land_main_code:  # 2015년에도 있었는데 없다고 판단된 주소 제거
    new_sub = new.loc[new.index.str.startswith(i)]
    old_sub = old.loc[old.index.str.startswith(i)&(old.index > new_sub.index[0])]
    if len(old_sub) == 0:  # 없다고 판단한 최소부번보다 큰 부번이 2015년에 없으면 정상
        continue
    elif old_sub.index[-1] > new_sub.index[-1]:  # 부번이 제일 높은 게 2015년에도 있다
        new = new.loc[~new.index.str.startswith(i)]  # 해당 본번은 2015년에 다 있었다
        print('erased '+i)
        # 3302220028,3302220065,3303020161
    else:  # 2015년에 남아있는 부번 최댓값보다 작은 부번은 사실 2015년에도 있었다  
        new = new.loc[~(new.index.str.startswith(i)&(new.index < old_sub.index[-1]))]
        print('truncatd '+i)
try: # 아래 지도로 국토교통부고시 제2019-298호 때에는 생기기 전이던 해창리 지번을 파악함
    base = gpd.read_file('gaori.gpkg', layer='block').explore(color='blue')
    new.loc[new['geometry'].notna(), :'2022_부번'].explore(
        color='red', m=base).save('after_20151118.html')
except ValueError:
    pass
new.reset_index(drop=True).loc[:, new.columns.str.startswith('2016')|
    new.columns.str.startswith('대장')|new.columns.str.startswith('법정동')
                               ].to_pickle('after_20151118.pk')
print(new.loc[new['geometry'].isna()]) # 궁리2지구, 종자관리소, 서정동393-16
