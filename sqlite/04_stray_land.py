"""
사생지의 부모 찾기 (등록전환을 중심으로)
"""
import pandas as pd
from sqlite3 import connect
stray_land = pd.read_csv('stray_land.txt',
                         sep='|', dtype=str, header=None,
                         names=['조서구분','생년','소재','법정동코드','대장구분','본번','부번'])
stray_land['고유번호'] = stray_land['법정동코드']+stray_land['대장구분']+\
                     stray_land['본번']+stray_land['부번']
stray_land = stray_land.set_index('고유번호').drop(
    columns=['법정동코드', '대장구분', '본번', '부번'])
movement_history = pd.read_csv(
    '../원자료옛자료/AL_41_D157_20220507.csv', dtype=str, keep_default_na=False,
    usecols=['고유번호', '토지이동이력순번', '지목', '토지면적',
             '토지이동사유', '토지이동일자']).set_index('고유번호')
movement_history = movement_history.loc[
    movement_history['토지이동일자'] >= '2015-11-18']
found_at_once = movement_history.merge(
    stray_land, left_index=True, right_index=True)
stray_land = stray_land.drop(index=found_at_once.index)
con = connect('gd.gpkg')
sql = "SELECT 법정동코드 || 대장구분 || 본번{new_year} || 부번{new_year} "\
      "FROM godeok LEFT JOIN code ON 소재{new_year}=법정동이름 "\
      "WHERE 소재{old_year}='{소재}' AND 대장구분='{대장구분}' "\
      "AND 본번{old_year}='{본번}' AND 부번{old_year}='{부번}'"
for i in stray_land.index:
    parameters = {'old_year':int(stray_land.loc[i, '생년']),
                  '소재': stray_land.loc[i, '소재'],
                  '대장구분': i[5],
                  '본번': i[6:10],
                  '부번': i[-4:]}
    parameters['new_year'] = parameters['old_year'] + 1
    response = pd.read_sql(sql.format(**parameters), con).squeeze()
    # assert isinstance(response, str)
    while response == i:
        parameters['new_year'] += 1
        response = pd.read_sql(sql.format(**parameters), con).squeeze()
        # except pd.io.sql.DatabaseError:
    stray_land.loc[i, '새번호'] = response
    stray_land.loc[i, '새해'] = str(parameters['new_year'])
con.close()
stray_land = stray_land.reset_index().set_index('새번호')
found_at_twice = movement_history.merge(
    stray_land, left_index=True, right_index=True)
stray_land = stray_land.drop(index=found_at_twice.index)
target = found_at_once.loc[ # 이 판단기준은 stray_land.txt에 관한 사전지식이 필요
    (found_at_once.index.str.startswith('330292')|
     found_at_once.index.str.startswith('3302910'))&
    found_at_once['토지이동사유'].str.contains('분할|전환', regex=True)].drop(
        columns=['생년', '소재', '조서구분'])
target = target.groupby('토지이동일자').filter(
    lambda x: (x['토지이동사유'].unique()!='번에서 분할').any())
target['현존여부'] = True
target = pd.concat([target, movement_history.loc[
    movement_history.index.str.startswith('33029')&
    movement_history['토지이동사유'].str.contains('전환', regex=False)]]
                   ).drop_duplicates(subset=['토지이동이력순번'],
                                     keep='first').fillna(False)
target = pd.concat([target, movement_history.loc[
    movement_history['토지이동사유'].str.contains('말소|분할', regex=True)].loc[
        target.index[target.index.str[5]=='1'].difference(
            target.index[target['현존여부']])]]
                   ).reset_index().set_index(
                       '토지이동이력순번').sort_index().fillna(False)
target['고유번호'] = target['고유번호'].str[5:]
target.drop(columns='현존여부').to_csv('등록전환.csv')
