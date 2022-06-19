"""
국토교통부 고시 제 2019-298호와 평택시 공고 제 2019-2393호의 비교분석
"""
import pandas as pd
locality = pd.read_excel('191001 고덕국제화계획지구 1단계_지번별조서(종전토지).xlsx',
                         header=1, index_col=0, usecols=[5,6,7], nrows=3140)
locality.loc[locality['지번'].str.startswith('산'),'대장구분'] = '2'
locality['대장구분'] = locality['대장구분'].fillna('1')
locality.loc[locality['대장구분']=='2','지번'] =\
            locality.loc[locality['대장구분']=='2','지번'].str[1:]
locality['본번'] = locality['지번'].str.split('-').apply(lambda x: x[0])
locality['부번'] = locality['지번'].str.split('-').apply(lambda x: x[1])
locality = locality.drop(columns=['지번'])
# 평택시 공고 제 2019-2393호의 지번별 조서 확정토지와 구분하려고 .0붙임
locality.columns = ['2019.0'+i for i in locality.columns]
molit = pd.read_csv('국토교통부고시제2019-298호_붙임1_정제.csv',
                    index_col=0, dtype=str)
molit_old = molit.groupby('연번').apply(lambda x: x.iloc[0,1:])
molit_old.columns = ['2018'+i for i in molit_old.columns]
molit_old = molit_old.reset_index()
# 중복은 추가변경(이미 변경된 필지의 재분할?) 때문에 생기는 듯
molit_new = molit.groupby('연번').apply(
    lambda x: x.iloc[1:,1:] if len(x)>1 else x.iloc[:1,1:]).drop_duplicates()
molit_new.columns = ['2019.0'+i for i in molit_new.columns]
molit_new = molit_new.reset_index('연번')
molit = molit_old.merge(molit_new, on=['연번'], how='left')
deathnote = molit.merge(locality, on=locality.columns.tolist(), how='inner')
molit.index = molit[locality.columns]
alive = molit[molit.index.isin(deathnote[locality.columns].to_records(index=False))\
              ==False]
print(len(molit)==len(deathnote)+len(alive))  # deathnote는 일대일대응이 됨
print(alive['2019.0소재지'].value_counts())
print(deathnote['2019.0소재지'].value_counts())
print(molit['2018소재지'].value_counts())
print(len(deathnote)==len(locality))  # 2019-2393호로 죽은 애들이 2019-298에 다 포함됨
