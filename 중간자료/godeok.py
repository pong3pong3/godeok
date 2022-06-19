"""
평택시 고덕지역 행정구역 변경내역 추적
"""
import geopandas as gpd
import pandas as pd
import numpy as np

upper_code = '41220'  # 평택시 시군구 코드
dictionary = pd.read_csv('법정동코드.tsv', sep='\t', dtype=str)  # 동코드-동이름

space = gpd.read_file('godeok.gpkg')  # 평택시 고덕면 및 고덕동 연속지적도
#print(len(space['SGG_OID'].unique())==len(space))  # 지적도 SGG_OID는 일대일대응

space['법정동코드'] = space['PNU'].apply(lambda x: x[5:10])
space['대장구분'] = space['PNU'].apply(lambda x: x[10])
space['2021_본번'] = space['PNU'].apply(lambda x: x[11:15])  # 2021년 말 현재
space['2021_부번'] = space['PNU'].apply(lambda x: x[15:])
space = space.drop(columns='PNU')
space= space.merge(dictionary, on='법정동코드', how='left').\
       drop(columns='법정동코드').rename(columns={'법정동이름':'2021_소재'})
print('최초길이')
print(len(space))
#print(space.dtypes['SGG_OID']==np.int64)  # 이때까지는 정수

# 평택시공고 제2021-3655호 (20-21)
change = pd.read_excel('211115 평택(송민) 행정구역 변경 지번별 내역서(고덕면 율포리 등 3개리_고덕동).xlsx',
                      header=[2,3], index_col=0).iloc[:,:-1]
change.columns = ['2020_소재','2020_본번','2020_부번',
                  '2021_소재','2021_본번','2021_부번',
                  '2021_지목','2021_면적']
change.loc[:,change.columns.str.endswith('번')] =\
    change.loc[:,change.columns.str.endswith('번')].astype(str)
# 대장구분이 불변함
#stationary = change[change['2021_본번'].str.startswith('산')].index==\
#     change[change['2020_본번'].str.startswith('산')].index
#print(stationary.all())
#print(len(stationary))
#print(
#    change.loc[:,change.columns.str.endswith('본번')].apply(
#	lambda x: x.apply(lambda y: y[0].isdigit())).value_counts()
#    )

change['대장구분'] = change['2021_본번'].apply(
    lambda x: '1' if x[0].isdigit() else '2')
change.loc[change['대장구분']=='2', ['2020_본번','2021_본번']] =\
    change.loc[change['대장구분']=='2', ['2020_본번','2021_본번']].apply(
        lambda x: x.apply(lambda y: y[1:]))
change.loc[:,change.columns.str.endswith('번')] =\
    change.loc[:,change.columns.str.endswith('번')].apply(
        lambda x: x.str.zfill(4))

space = space.merge(change,
                    on=['대장구분','2021_소재','2021_본번','2021_부번'],
                    how='outer')
# 고덕동 또는 서정동 607-12인 경우는 신규토지로 규정
space.loc[space['2020_소재'].isna()&(space['2021_소재']!='고덕동'),
          ['2020_소재','2020_본번','2020_부번']] =\
    space.loc[space['2020_소재'].isna()&(space['2021_소재']!='고덕동'),
              ['2021_소재','2021_본번','2021_부번']].values
space.loc[(space['2021_소재']=='서정동')&
          (space['2021_본번']=='0607')&
          (space['대장구분']=='1')&
          (space['2021_부번']=='0012'),
          ['2020_소재','2020_본번','2020_부번']] = np.nan
print('고덕동 신설당시 길이')
print(len(space))
#print(space.dtypes['SGG_OID']==np.int64)  # 여기서부터 NA발생 때문에 소수로 변경

# 평택시공고 제2021-1008호 (20-21)
# 평택시공고 제2021-1008호 지번별조서의 확정토지(산 없음)보다 본번이 크거나 같고
# 산이 아니면 신규토지로 규정
space.loc[(space['2020_소재']=='고덕면 궁리')&(space['대장구분']=='1')\
          &(space['2020_본번']>'0521'),
          ['2020_소재','2020_본번','2020_부번']] = np.nan
legacy = pd.read_excel('210323 궁리2지구 지구단위계획(종전토지).xlsx',
                       header=4, usecols=[0,2,3,4,5,6],
                       names=['분류','면','리','지번','2020_지목','2020_면적'])
tmp = 0
for i in legacy.loc[legacy['분류']=='소 계'].index:
    legacy['분류'].iloc[tmp:i] = legacy['분류'].iloc[tmp:i].dropna().squeeze()
    tmp = i+1
legacy = legacy.loc[legacy['분류'].str.endswith('계')==False]
for i,j in enumerate([4,5,3]):
    legacy.loc[legacy['분류']==legacy['분류'].unique()[i],'말소'] = str(j)
#print(legacy['지번'].str.contains(' ').any())
legacy.loc[legacy['지번'].str.startswith('산'),'대장구분'] = '2'
legacy['대장구분'] = legacy['대장구분'].fillna('1')
legacy['2020_소재'] = legacy['면']+'면 '+legacy['리']+'리'
legacy.loc[legacy['대장구분']=='2','지번'] = \
        legacy.loc[legacy['대장구분']=='2','지번'].str[1:]
legacy['2020_본번'] = legacy['지번'].str.split('-').apply(
    lambda x: x[0]).str.zfill(4)
legacy['2020_부번'] = legacy['지번'].str.split('-').apply(
    lambda x: x[1] if len(x)==2 else '0').str.zfill(4)
space = pd.concat([space,
                   legacy.drop(columns=['분류','면','리','지번'])])
print('궁리2지구 종전토지 포함 길이')
print(len(space))

# 평택시공고 제2020-86호 (19-20)
change = pd.read_excel('200110 평택(송민) 지번별조서(고덕국제화계획지구 행정구역변경 2차).xlsx',
                      header=[2,3], index_col=0, sheet_name='고덕신도시 2,3단계(율포리 편입)').\
                      drop(index='합계').iloc[:,:-2]
change = pd.concat([change,
                    pd.read_excel('200110 평택(송민) 지번별조서(고덕국제화계획지구 행정구역변경 2차).xlsx',
                      header=[2,3], index_col=0, sheet_name='고덕신도시 2,3단계(좌교리 편입)').\
                      drop(index='합계').iloc[:,:-2]])
change.columns = ['2019_소재','2019_지번','2020_소재',
                  '2020_지번','2020_지목(임시)','2020_면적(임시)']
change.loc[:,change.columns.str.endswith('번')] =\
    change.loc[:,change.columns.str.endswith('번')].astype(str)
# 대장구분이 불변함
#stationary = change[change['2020_지번'].str.startswith('산')].index==\
#     change[change['2019_지번'].str.startswith('산')].index
#print(stationary.all())
#print(len(stationary))
#print(
#    change.loc[:,change.columns.str.endswith('지번')].apply(
#	lambda x: x.apply(lambda y: y[0].isdigit())).value_counts()
#    )

change['대장구분'] = change['2020_지번'].apply(
    lambda x: '1' if x[0].isdigit() else '2')
change['2019_본번'] = change['2019_지번'].str.split('-').apply(
    lambda x: x[0].lstrip('산'))
change['2020_본번'] = change['2020_지번'].str.split('-').apply(
    lambda x: x[0].lstrip('산'))
change['2019_부번'] = change['2019_지번'].str.split('-').apply(
    lambda x: x[-1] if len(x)==2 else '0')
change['2020_부번'] = change['2020_지번'].str.split('-').apply(
    lambda x: x[-1] if len(x)==2 else '0')
change = change.drop(columns=['2019_지번','2020_지번'])
change.loc[:,change.columns.str.endswith('번')] =\
    change.loc[:,change.columns.str.endswith('번')].apply(
        lambda x: x.str.zfill(4))

space = space.merge(change,
                    on=['대장구분','2020_소재','2020_본번','2020_부번'],
                    how='outer')
space.loc[space['2020_지목'].isna(),['2020_지목','2020_면적']] =\
    space.loc[space['2020_지목'].isna(),['2020_지목(임시)','2020_면적(임시)']].values
space = space.drop(columns=['2020_지목(임시)','2020_면적(임시)'])
# 좌교리와 율포리의 대장구분마다 평택시공고 제2020-86호 지번별조서의 확정토지 본번 최솟값을 구함
# 좌교리와 율포리의 본번이 이 최솟값 이상이면 확정토지 이후의 신규토지로 규정
for i in range(1,3):
    for j in ('고덕면 좌교리','고덕면 율포리'):
        threshold = change.loc[(change['2020_소재']==j)&(change['대장구분']==str(i)),
                               '2020_본번'].min()
        space.loc[(space['2019_소재'].isna())&(space['대장구분']==str(i))&\
                  (space['2020_소재']==j)&(space['2020_본번']>=threshold),
                  '2019_소재'] = '(신규)'
space.loc[space['2019_소재'].isna(),['2019_소재','2019_부번','2019_본번']] =\
    space.loc[space['2019_소재'].isna(),['2020_소재','2020_부번','2020_본번']].values
space['2019_소재'] = space['2019_소재'].replace('(신규)',np.nan)
print('고덕국제화계획지구 내 경계조정 전 길이')
print(len(space))

# 평택시공고 제2019-3104호, 평택시공고 제2019-2393호 (18-19)
news = pd.read_excel('191217 경기도종자관리소 종자생산시설_지번별조서(확정토지).xlsx',
                     header=2, index_col=0).iloc[:,:-1]
news['등록'] = '2'
news = pd.concat([news,
                  pd.read_excel('191001 고덕국제화계획지구 1단계_지번별조서(확정토지).xlsx',
                                header=2, index_col=0, sheet_name='여염리')\
                  .iloc[:,:-1],
                  pd.read_excel('191001 고덕국제화계획지구 1단계_지번별조서(확정토지).xlsx',
                                header=2, index_col=0, sheet_name='해창리')\
                  .iloc[:,:-1]]).dropna(subset=['소재지'])
news.loc[news['등록'].isna(),'등록'] = '1'
news.columns = ['소재','지번','2019_지목','2019_면적','등록']
news['지번'] = news['지번'].astype(str)
#print(news['지번'].str.startswith('산').any())
news['대장구분'] = '1'
news['본번'] = news['지번'].str.split('-').apply(lambda x: x[0].zfill(4))
news['부번'] = news['지번'].str.split('-').apply(
    lambda x: x[-1].zfill(4) if len(x)==2 else '0000')
news = news.drop(columns='지번')

space = space.merge(news,
                    left_on=['2019_소재','2019_본번','2019_부번','대장구분'],
                    right_on=['소재','본번','부번','대장구분'],
                    how='outer').drop(columns=['소재','본번','부번'])
print('여염리 동고리 신규지번 확인 후 길이')
print(len(space))

legacy1 = pd.read_excel('191001 고덕국제화계획지구 1단계_지번별조서(종전토지).xlsx',
                         header=1, usecols=[6,7,8,9], nrows=3140)
legacy1['말소'] = '1'
legacy1.columns = ['2018_소재','지번','2018_지목','2018_면적','말소']
legacy2 = pd.read_excel('191217 경기도종자관리소 종자생산시설_지번별조서(종전토지).xlsx',
                        header=2).iloc[:,1:-1].dropna()
legacy2['말소'] = '2'
legacy2.columns = legacy1.columns
legacy2['2018_소재'] = legacy2['2018_소재'].str.replace('고덕면','고덕면 ')
legacy = pd.concat([legacy1, legacy2]); del legacy1, legacy2

legacy.loc[legacy['지번'].str.startswith('산'),'대장구분'] = '2'
legacy['대장구분'] = legacy['대장구분'].fillna('1')
legacy.loc[legacy['대장구분']=='2','지번'] =\
            legacy.loc[legacy['대장구분']=='2','지번'].str[1:]
legacy['2018_본번'] = legacy['지번'].str.split('-').apply(lambda x: x[0].zfill(4))
legacy['2018_부번'] = legacy['지번'].str.split('-').apply(lambda x: x[1].zfill(4))
legacy = legacy.drop(columns='지번')
#print(legacy['2018_소재'].str.startswith('고덕면').all())

space = pd.concat([space,legacy])
# 평택시공고 제2019-3104호, 평택시공고 제2019-2393호 지번별조서 확정토지(산 없음)의
# 각 법정리별 본번의 최솟값 이상이면서 지번별조서에 없고, 산이 아니면 신규토지로 규정
threshold = news.groupby('소재')['본번'].min()
for i in threshold.index:
    space.loc[(space['2019_소재']==i)&(space['2019_본번']>=threshold[i])
              &(space['등록'].isna())&(space['대장구분']=='1'), '2018_소재'] = '(신규)'
space.loc[(space['2018_소재'].isna())&(space['등록'].isna()),
          ['2018_소재','2018_부번','2018_본번']] =\
    space.loc[(space['2018_소재'].isna())&(space['등록'].isna()),
              ['2019_소재','2019_부번','2019_본번']].values
space['2018_소재'] = space['2018_소재'].replace('(신규)',np.nan)
print('여염리 동고리 종전토지 포함 길이')
print(len(space))

# 국토교통부고시 제2019-298호 (17-18)
molit = pd.read_csv('국토교통부고시제2019-298호_붙임1_정제.csv',
                    index_col=0, dtype=str).rename(columns={'소재지':'소재'})
molit[['본번','부번']] = molit[['본번','부번']].apply(lambda x: x.str.zfill(4))
molit_old = molit.groupby('연번').apply(lambda x: x.iloc[0,1:])
molit_old.columns = ['2017_'+i for i in molit_old.columns]
molit_old = molit_old.reset_index()

molit_new = molit.groupby('연번').apply(
    lambda x: x.iloc[1:,1:] if len(x)>1 else x.iloc[:1,1:]).drop_duplicates()
molit_new.columns = ['2018_'+i for i in molit_new.columns]
molit_new = molit_new.reset_index('연번')
molit = molit_old.merge(molit_new, on=['연번'], how='left'); del molit_new, molit_old
#print(len(molit.groupby('연번').filter(
#    lambda x: (x['2017_대장구분']!=x['2018_대장구분']).any()))==0)
molit = molit.rename(columns={'2018_대장구분':'대장구분'}).drop(columns='2017_대장구분')

# 당현리534-1처럼 정상적인 경우라면 여염리3581로 한번에 변경되어 outer merge시 행수 유지
# 그러나 국토교통부고시 연번472의 당현리534는 당현리534와 당현리534-2로 분할됐는데,
# 당현리534-2가 여염리3882로 추가변경되어 당현리534-2가 outer merge시 행수를 늘림.
# 당현리534-2의 옛지번이었던 당현리534를 stray폴더의 2015년 지도에서 확인가능.
# 행수가 늘어나는 건 이런 경우(연번1921, 연번1924 등)라 outer에서 left로 merge 방법 변경
space = space.merge(molit.drop(columns='연번'), how='left',
                    on=['2018_소재','2018_본번','2018_부번','대장구분'])
# 2021년 11월 기준 국제화계획지구 및 택지개발지구와 겹친 해창리거나
# 고덕동이면서 일반산업단지가 아니(평택시고시 제2017-427호 관련)었던 곳 가운데
# 국토교통부고시 제2019-298호 붙임1에 없으면 신규토지로 규정
# (본래 고덕동 + 2018년 좌교리로 조건이 좁았었음)
# (국제화계획지구 및 택지개발지구서 geometry.isna며 15년말 이후생성은 서정동393-16뿐)
#from shapely.geometry import Polygon
#gpd.GeoDataFrame(geometry=gpd.read_file('고덕_국제화계획지구_및_택지개발지구_(기준고시202111).gpkg')
#                 [['geometry']].dissolve().to_crs(space.crs)['geometry'].apply(
#                     lambda x: Polygon(x.exterior)).buffer(-1)).sjoin(
#                     space.loc[space['2017_소재'].isna()&
#                               (space['2018_소재']=='고덕면 해창리')&
#                               (space['2021_소재']=='고덕면 해창리'),
#                               ['2018_소재','대장구분','2018_본번','2018_부번',
#                                'SGG_OID','geometry']]
#                     ).drop(columns=['geometry', 'index_right']).set_index(
#                         'SGG_OID').sort_index()
# 위 공간연산 결과에서 아래 두 지번이 삭제/추가됨:
# 해창리 산76-3(855059)은 국토교통부고시 제2019-298호 붙임1에서 누락된 듯 하므로 신규 X,
# 해창리 785-11(3275409)은 해창리785-10이 이미 신규이므로 신규 O
space.loc[space['SGG_OID'].isin(
    [2663841, 2663974, 2663975, 2663976, 2663977, 3275400, 3275402, 3275404,
     3275406, 3275408, 3275409, 3275411, 3275413, 3275415, 3276294, 3276296,
     3276298, 3276300, 3276302, 3276304]), '2017_소재'] = '(신규)'
#print(sorted(
#    space.loc[space['2017_소재'].isna()&(space['2021_소재']=='고덕동')&
#    (space['2018_소재']=='고덕면 여염리'), '2018_본번'].unique())
space.loc[space['2017_소재'].isna()&space['2018_소재'].notna()&
          (space['2021_소재']=='고덕동')&(space['2018_소재']!='고덕면 여염리'),
          '2017_소재'] = '(신규)'
# (신규)로 판단된 토지 가운데 사실은 신규가 아니었던 토지 정정
legacy = space.loc[space['2017_소재'].notna()&(space['2017_소재']!='(신규)')].groupby(
    ['2018_소재', '대장구분', '2018_본번'])['2018_부번'].max().rename('max_legacy')
news = space.loc[space['2017_소재']=='(신규)'].groupby(
    ['2018_소재', '대장구분', '2018_본번'])['2018_부번'].min().rename('min_news')
compare = pd.merge(news, legacy, left_index=True, right_index=True, how='inner')
compare = compare.loc[compare['max_legacy'] > compare['min_news']]
for i in compare.index:
    space.loc[(space['2018_소재']==i[0])&(space['대장구분']==i[1])&
              (space['2018_본번']==i[2])&(space['2017_소재']=='(신규)')&
              (space['2018_부번'] < compare.loc[i, 'max_legacy']),
              '2017_소재'] = np.nan
space.loc[space['2017_소재'].isna(),['2017_소재','2017_부번','2017_본번']] =\
    space.loc[space['2017_소재'].isna(),['2018_소재','2018_부번','2018_본번']].values
space['2017_소재'] = space['2017_소재'].replace('(신규)',np.nan)
# 한 번도 고덕동 또는 고덕면이 아닌 행 제거 (서정동 월경지 제외)
space = space.loc[
    space.loc[:,space.columns.str.endswith('소재')].apply(
        lambda x: x.str.startswith('고덕').any(), axis=1)|
    space['SGG_OID'].notna()]
print('국토교통부고시에 따른 경계조정 전 길이')
print(len(space))

# 평택시고시 제2017-427호 (16-17)
news = pd.read_excel('고덕국제화지구 일반산업단지 확정토지 지번별 면적조서.xlsx',
                     header=1).iloc[:-1,:-1]
news.columns = ['소재','지번','2017_지목','2017_면적']
news['소재'] = news['소재'].apply(lambda x: x[4:])
news['지번'] = news['지번'].astype(str).apply(lambda x: x[:-2])
#print(news['지번'].str.startswith('산').any())
news['대장구분'] = '1'
#print(news['지번'].str.contains('-').any())
news['부번'] = '0000'
news = news.rename(columns={'지번':'본번'})
news['등록(임시)'] = '0'

space = space.merge(news,
                    left_on=['2017_소재','2017_본번','2017_부번','대장구분'],
                    right_on=['소재','본번','부번','대장구분'],
                    how='outer').drop(columns=['소재','본번','부번'])
space.loc[space['등록'].isna(),'등록'] =\
    space.loc[space['등록'].isna(),'등록(임시)'].values
space = space.drop(columns=['등록(임시)'])
print('산업단지 신규지번 확인 후 길이')
print(len(space))

legacy = pd.read_excel('고덕국제화지구 일반산업단지 종전토지 지번별 면적조서.xlsx',
                     header=1, nrows=2454, sheet_name='종전토지조서').iloc[:,1:5]
legacy.columns = ['2016_소재','지번','2016_지목','2016_면적']
legacy['말소'] = '0'
legacy['지번'] = legacy['지번'].astype(str).str.lstrip(' ')
legacy.loc[legacy['지번'].str.startswith('산'),'대장구분'] = '2'
legacy['대장구분'] = legacy['대장구분'].fillna('1')
legacy.loc[legacy['대장구분']=='2','지번'] = \
    legacy.loc[legacy['대장구분']=='2','지번'].str[1:]
legacy['2016_본번'] = legacy['지번'].str.split('-').apply(lambda x: x[0].zfill(4))
legacy['2016_부번'] = legacy['지번'].str.split('-').apply(
    lambda x: x[1].zfill(4) if len(x)==2 else '0000')

space = pd.concat([space,legacy.drop(columns='지번')])
# 산이 아닌 여염리 가운데 평택시고시 제2017-427호 지번별조서의
# 확정토지 본번 최솟값 이상인 지번은 신규토지로 규정
# 서정동 607-11인 경우도 신규토지로 규정
#print(news['본번'].apply(len).unique()==4)
space.loc[(space['2017_소재']=='고덕면 여염리')&(space['2017_본번']>=news['본번'].min())\
          &(space['대장구분']=='1'),
          '2016_소재'] = '(신규)'
space.loc[(space['2017_소재']=='서정동')&(space['2017_본번']=='0607')\
          &(space['대장구분']=='1')&(space['2017_부번']=='0011'),
          '2016_소재'] = '(신규)'
space.loc[space['2016_소재'].isna(),
          ['2016_소재','2016_부번','2016_본번']] =\
    space.loc[space['2016_소재'].isna(),
              ['2017_소재','2017_부번','2017_본번']].values
space['2016_소재'] = space['2016_소재'].replace('(신규)',np.nan)
print('산업단지 종전토지 포함 길이')
print(len(space))

# 평택시고시 제2017-229호 (38번국도~신리 도로공사로 신규 지번)
# news = pd.read_pickle('중로1-80.pk')
# space = space.merge(news, on=['대장구분','2017_소재','2017_본번'], how='left')
# target = space['최소_부번'].notna()&(space['최소_부번']<=space['2017_부번'])
# space.loc[target, ['2016_소재','2016_본번','2016_부번']] = np.nan
# space = space.drop(columns=['최소_부번'])

# 평택시공고 제2021-1008호 지번별조서의 확정토지
space.loc[(space['2021_소재']=='고덕면 궁리')&(space['대장구분']=='1')\
          &(space['2021_본번']=='0522')&(space['2021_부번']=='0000'),
          ['등록','2021_지목','2021_면적']] = ['3','도',897.6]
space.loc[(space['2021_소재']=='고덕면 궁리')&(space['대장구분']=='1')\
          &(space['2021_본번']=='0523')&(space['2021_부번']=='0000'),
          ['등록','2021_지목','2021_면적']] = ['4','대',90897.3]
space.loc[(space['2021_소재']=='고덕면 궁리')&(space['대장구분']=='1')\
          &(space['2021_본번']=='0524')&(space['2021_부번']=='0000'),
          ['등록','2021_지목','2021_면적']] = ['5','공',17587.]
space.loc[(space['2021_소재']=='고덕면 궁리')&(space['대장구분']=='1')\
          &(space['2021_본번']=='0525')&(space['2021_부번']=='0000'),
          ['등록','2021_지목','2021_면적']] = ['5','도',1200.6]

# 소수로 바뀐 SGG_OID를 정수형태의 문자로 변경
space.loc[space['SGG_OID'].notna(),'SGG_OID'] =\
    space.loc[space['SGG_OID'].notna(),'SGG_OID'].astype(str).str[:-2]
print(space.columns)

# 평택시조례 제1531호, 평택시조례 제1638호
border = pd.read_pickle('boundary.pk')
#print(boder.index.duplicatd().any()) # 한 확정토지가 여러 종전토지에 대응되지 않음
space = space.merge(border, how='left', on='SGG_OID')
target = space['A1'].notna()
space.loc[target,[0,1,2,3]] = space.loc[target,'A1'].str.extract(
    upper_code+'(\d{5,5})(\d{1,1})(\d{4,4})(\d{4,4})')
#print((space.loc[target,'대장구분']==space.loc[target,1]).all())
space = space.merge(dictionary, how='left', left_on=0, right_on='법정동코드').\
        rename(columns={'법정동이름':'소재',2:'본번',3:'부번'}).drop(
            columns=[0,1,'법정동코드','A1'])
for i in space['changed_year'].unique():
    if type(i)!=str:
        continue
    for j in ('소재','본번','부번'):
        columns_to_update = space.columns[
            space.columns.str[:4].str.isdigit()&
            (space.columns.str[:4]<i)&
            space.columns.str.endswith(j)]
        for k in columns_to_update:
            space.loc[space['changed_year']==i,k]=\
                space.loc[space['changed_year']==i,j].values
space = space.drop(columns=['changed_year','소재','본번','부번'])

# 가장 오래된 연속지적도 (15-16)
try:
    news = pd.read_pickle('after_20151118.pk')
    before = len(space)
    space = space.merge(news,
                        on=['대장구분','2016_소재','2016_본번','2016_부번'], how='left')
    assert before==len(space)
    space.loc[space['법정동코드'].isna(),
              ['2015_소재','2015_부번','2015_본번']] =\
              space.loc[space['법정동코드'].isna(),
                        ['2016_소재','2016_부번','2016_본번']].values
    space = space.drop(columns=['법정동코드'])
except FileNotFoundError: # after_20151118.py를 실행하기 전
    sort = [str(i)+'_'+j for i in range(2021,2015,-1)\
        for j in ('소재','본번','부번','지목','면적')]
    space = space[['대장구분']+sort+['등록','말소','JIBUN','BCHK','SGG_OID',
                                 'geometry']]
    space.to_file('gaori.gpkg', driver='GPKG')
    raise EOFError

# 평택시조례 제1267호 (14-15)
change = pd.read_pickle('평택시조례_제1267호.pk')
before = len(space)
space = space.merge(change,
                    on=['대장구분','2015_소재','2015_본번','2015_부번'], how='outer')
assert before==len(space)
space.loc[space['2014_소재'].isna(),
          ['2014_소재','2014_부번','2014_본번']] =\
    space.loc[space['2014_소재'].isna(),
              ['2015_소재','2015_부번','2015_본번']].values
space[['2015_지목', '2015_면적']] = np.nan # 다른 연도와 일관되도록 새로운 빈 열 생성

# 평택시공고 제2022-549호 (21-22)
legacy = pd.read_excel('220216 평택(송민) 종전토지(폐쇄) 지번별 조서.xlsx',
                       header=4, index_col=0,
                       names=['2021_소재','지번','지목','면적','소유자','비고']
                       ).iloc[:-1,:-2]
legacy['대장구분'] = legacy['지번'].apply(
    lambda x: '2' if x[0]=='산' else '1')
legacy['2021_본번'] = legacy['지번'].str.split('-').apply(
    lambda x: x[0]).str.lstrip('산').str.zfill(4)
legacy['2021_부번'] = legacy['지번'].str.split('-').apply(
    lambda x: x[1].zfill(4) if len(x)==2 else '0000')
legacy['2021_소재'] = legacy['2021_소재'].str.replace('해창리',' 해창리')

space = space.merge(legacy,
                    on=['대장구분','2021_소재','2021_본번','2021_부번'],
                    how='left')
target = space['지번'].notna()
assert len(legacy)==target.value_counts()[True]
space.loc[target,'말소'] = '6'
space.loc[target&(space['2021_소재']=='고덕면 해창리'),
          ['2021_지목','2021_면적']] =\
space.loc[target&(space['2021_소재']=='고덕면 해창리'),
          ['지목','면적']].values
space = space.drop(columns=['지번','지목','면적'])

news = pd.read_excel('220216 평택(송민) 확정토지 지번별 조서.xlsx',
                     header=5, index_col=0,
                     names=['2022_소재','지번','2022_지목','2022_면적',
                            '소유자','용도','구분1','구분2','비고']).iloc[:-1]
assert news['지번'].str[0].str.isdigit().all()
news['대장구분'] = '1'
news['2022_본번'] = news['지번'].astype(str).str.split('-').apply(
    lambda x: x[0]).str.lstrip('산').str.zfill(4)
news['2022_부번'] = news['지번'].astype(str).str.split('-').apply(
    lambda x: x[1].zfill(4) if len(x)==2 else '0000')
news = news.drop(columns=['지번','소유자','비고']).rename(columns={
    '용도':'blockTYPE','구분1':'blockNAME','구분2':'blockJIBUN'})
news['등록'] = '6'

space = pd.concat([space, news])
space.loc[space['2021_소재'].notna()&space['말소'].isna(),
          ['2022_소재','2022_본번','2022_부번']] =\
    space.loc[space['2021_소재'].notna()&space['말소'].isna(),
          ['2021_소재','2021_본번','2021_부번']].values

sort = [str(i)+'_'+j for i in range(2022,2013,-1)\
        for j in ('소재','본번','부번','지목','면적')]
space = space[['대장구분']+sort+['등록','말소','JIBUN','BCHK','SGG_OID',
                             'blockTYPE','blockNAME','blockJIBUN','geometry']]
space.to_file('gaori.gpkg', driver='GPKG')

# 토지이용계획도
block = gpd.read_file('고덕_국제화계획지구_및_택지개발지구_(기준고시202111).gpkg').\
        to_crs(space.crs)
block.to_file('gaori.gpkg', driver='GPKG', layer='block')
