"""
csv로 변환한 국토교통부 고시 제 2019-298호의 붙임 1을 정제
"""
import pandas as pd
import re
df = pd.read_csv('국토교통부고시제2019-298호_붙임1.csv',
                 header=None, dtype=str).fillna('')
rawrow = len(df)
df.iloc[4164,0] = '2558'
print(df.iloc[7123])
df.iloc[7147,2] = '경기도 평택시\n고덕면 좌교리'
df.iloc[7174,2] = '경기도 평택시\n고덕면 좌교리'
df = df[df.apply(lambda x: x.str.contains('경기도 평택시').any(),
                 axis=1)]
print(rawrow-len(df)==677*2+3)
df_index = df[(df[0].str.contains('기정'))|
              (df[1].str.contains('기정'))]
number = re.compile('\d+')
df_index = df_index.apply(lambda x:
                          number.search(
                              x.to_string(index=False)).group(0),
                          axis=1)
for i in df.index:
    try:
        df.loc[i,'연번'] = df_index.loc[i]
    except KeyError:
        df.loc[i,'연번'] = df_index.loc[df_index.index[df_index.index<i].max()]
df['소재지'] = df[2].apply(lambda x: x.split('\n')[-1])
df.loc[df[3].str.contains('산'),'대장구분'] = '2'
df['대장구분'] = df['대장구분'].fillna('1')
df['본번'] = df.loc[:,3:4].apply(lambda x:
                               number.search(
                                   x.to_string(index=False)).group(0),
                               axis=1)
df['부번'] = df[5].replace('','0')
df[['연번','소재지','대장구분','본번','부번']].to_csv('국토교통부고시제2019-298호_붙임1_정제.csv')
