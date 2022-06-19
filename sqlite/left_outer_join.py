"""
해창리 지도의 구멍을 주제로 토지이동이력정보 튜토리얼
"""
import pandas as pd
from sqlite3 import connect
from collections import Counter
con = connect('gd.gpkg')
candidate = pd.read_sql("SELECT 대장구분, 본번2018, 부번2018 , 부번2017 "\
                        "FROM godeok WHERE 조서구분='1' AND "\
                        "소재2018='고덕면 해창리' AND 소재2021 IS NULL AND "\
                        "부번2018<>부번2017", con)
con.close()
left_outer_join = pd.read_csv('left_outer_join.txt',
                              sep='|', dtype=str, header=None,
                              usecols=[0], names=['고유번호']).squeeze().str[5:]
candidate = candidate.loc[(candidate['대장구분']+candidate['본번2018']+
                           candidate['부번2017']).isin(left_outer_join)]
assert len(left_outer_join) == Counter(
    candidate[['본번2018','부번2017']].duplicated())[False]
candidate = candidate['대장구분']+candidate['본번2018']+candidate['부번2018']
movement_history = pd.read_csv('../원자료옛자료/AL_41_D157_20220507.csv',
                               dtype=str, usecols=['고유번호', '토지이력순번',
                                '토지면적', '토지이동사유', '토지이동일자'])
movement_history = movement_history.loc[
    movement_history['고유번호'].str.startswith('33025')].set_index('고유번호')
movement_history.index = movement_history.index.str[5:]
assert ~candidate.isin(movement_history.index).any()
movement_history = movement_history.loc[
    movement_history.index.isin(left_outer_join)&
    (movement_history['토지이동일자'] >= '2018-01-01')]
print(movement_history['토지이동사유'].unique())
