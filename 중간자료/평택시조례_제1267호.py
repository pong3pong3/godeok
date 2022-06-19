"""
평택시조례 제1267호 지번별 조서 생성
"""
import pandas as pd
import numpy as np
from collections import Counter

legacy = pd.read_excel('고덕국제화지구 일반산업단지 종전토지 지번별 면적조서.xlsx',
                     header=1, nrows=2454, sheet_name='종전토지조서').iloc[:,1:5]
legacy.columns = ['2016_소재','지번','2016_지목','2016_면적']
legacy['지번'] = legacy['지번'].astype(str).str.lstrip(' ')
legacy.loc[legacy['지번'].str.startswith('산'),'대장구분'] = '2'
legacy['대장구분'] = legacy['대장구분'].fillna('1')
legacy.loc[legacy['대장구분']=='2','지번'] = \
    legacy.loc[legacy['대장구분']=='2','지번'].str[1:]
legacy['2016_본번'] = legacy['지번'].str.split('-').apply(lambda x: x[0].zfill(4))
legacy['2016_부번'] = legacy['지번'].str.split('-').apply(
    lambda x: x[1].zfill(4) if len(x)==2 else '0000')

change = pd.read_csv('평택시공고제2015-849호_참고2.csv', header=None, dtype=str,
                     names=['연번','2014_소재','지번','2014_지목','2014_면적'])
change = change.loc[change['2014_소재'].notna()]
change = change.apply(lambda x: x.str.strip(' ').str.replace('  ',' '))
change['2014_면적'] = pd.to_numeric(change['2014_면적'].str.replace(',',''))
change.loc[change['지번'].str.startswith('산'),'대장구분'] = '2'
change['대장구분'] = change['대장구분'].fillna('1')
change.loc[change['대장구분']=='2','지번'] = \
    change.loc[change['대장구분']=='2','지번'].str[1:]
change['2014_본번'] = change['지번'].str.split('-').apply(lambda x: x[0].zfill(4))
change['2014_부번'] = change['지번'].str.split('-').apply(
    lambda x: x[1].zfill(4) if len(x)==2 else '0000')
for i,j in enumerate(['고덕면 궁리','고덕면 방축리','장당동','모곡동','지제동']):
    change.loc[change['2014_소재']==j, 'custom_order']=i
change = change.sort_values(
    by=['대장구분','custom_order','2014_본번','2014_부번']
    ).reset_index(drop=True)
change = change.drop(columns=['지번', 'custom_order', '연번'])

legacy = pd.concat([legacy.iloc[898:2089],
                    legacy.iloc[2285:]]).reset_index(drop=True)
assert legacy['대장구분'].is_monotonic_increasing
assert Counter(change['대장구분']=='2')[True] == Counter(legacy['대장구분']=='2')[True]
legacy = legacy.drop(columns=['지번', '대장구분'])
legacy.columns = legacy.columns.str.replace('2016','2015')
res1 = pd.concat([change.iloc[:183], legacy.iloc[:183]], axis=1)
change = pd.concat([change, pd.DataFrame(
    index=[1+i+max(change.index) for i in range(3)])])
res2 = pd.concat([change.iloc[964:].shift(3), legacy.iloc[967:]],
                 axis=1).dropna(axis='index', how='all')
change = change.iloc[183:964]
legacy = legacy.iloc[183:967]
res3 = change.loc[change['2014_지목']=='유'].merge(
    legacy.loc[legacy['2015_지목']=='유'],
    left_on=['2014_지목'], right_on=['2015_지목'])
change = change.loc[change['2014_지목']!='유'].reset_index(drop=True)
legacy = legacy.loc[legacy['2015_지목']!='유'].reset_index(drop=True)
res4 = pd.concat([change.iloc[:518], legacy.iloc[:518]], axis=1)
change = change.iloc[518:]
change = change.reindex(np.roll(change.index, 1))
change.index = sorted(change.index)
change.loc[518, '2014_본번'] = '0308' # 308번지를 3085로 오타친 듯
res5 = pd.concat([change, legacy.iloc[518:]], axis=1)
res = pd.concat([res1, res2, res3, res4, res5]).reset_index(drop=True)
assert (res['2014_지목']==res['2015_지목']).all()
print(res.loc[res['2014_면적']!=res['2015_면적']])
res.drop(columns=['2015_면적','2015_지목']).to_pickle('평택시조례_제1267호.pk')
