"""
2020년에서 2019년으로 거슬러갈 때 연결이 끊겼던 주소를
SQL로 이어준 뒤 변화를 비교
"""
import pandas as pd
from sqlite3 import connect
con = connect('gd.gpkg')
sql = 'SELECT * FROM godeok'
new = pd.read_sql(sql, con)
con.close()
con = connect('veiled_gd.gpkg')
old = pd.read_sql(sql, con)
con.close()
old['is_old'] = True
new['is_new'] = True
df = new.merge(old, how='outer').set_index(['대장구분', '소재2020', '본번2020'])
assert len(old) == len(new)
assert (old['소재2019'].isna()&old['소재2020'].notna()).value_counts()[True]\
       == df['is_old'].isna().value_counts()[True]
tmp = df.loc[df['is_new'].notna()]
tmp = tmp.loc[tmp.index[tmp['is_old'].isna()].unique()].reset_index()
tmp = tmp.drop(columns=['지목', '면적', '소재2022', '본번2022', '부번2022',
                        '소재2021', '본번2021', '부번2021', '등록전환구분',
                        'is_new', 'is_old'])
