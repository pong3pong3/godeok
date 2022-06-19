"""
gaori.gpkg의 한글값들을 코드/영문화하고 지목이나 면적은 빼서 ray.gpkg로 저장
"""
import geopandas as gpd
import pandas as pd
import sqlite3

gdf = gpd.read_file('gaori.gpkg')
gdf.columns = gdf.columns.str.replace('소재','village_code').\
              str.replace('등록','register_order').str.replace('말소','cancellation_order').\
              str.replace('본번','land_main_code').str.replace('부번','land_sub_code').\
              str.replace('대장구분','ledger_code').str.replace('NAME','_name').\
              str.replace('TYPE','_type_name').str.replace('blockJIBUN','block_land_code')
gdf = gdf.loc[:,gdf.columns.str.endswith('code')|
                gdf.columns.str.endswith('order')|
                gdf.columns.str.endswith('geometry')|
                gdf.columns.str.startswith('block')]
gdf.columns = list(map(lambda x: x[5:]+'_'+x[:4] if x[0].isdigit() else x,
                       gdf.columns.tolist()))
dictionary = pd.read_csv('중간자료/법정동코드.tsv', sep='\t', dtype=str,
                         header=0, names=['village_code','village_name'])
for i in range(len(dictionary)):
    gdf=gdf.replace(dictionary.iloc[i]['village_name'],
                    dictionary.iloc[i]['village_code'])
gdf.to_file('ray.gpkg',driver='GPKG')

con = sqlite3.connect('ray.gpkg')
cur = con.cursor()
cur.execute('''CREATE TABLE village_code_table
(village_code TEXT, village_name TEXT)''')
cur.executemany('INSERT INTO village_code_table VALUES (?, ?)',
                dictionary.to_records(index=False))
con.commit()
con.close()

gdf = gpd.read_file('gaori.gpkg', layer='block')
dictionary = pd.read_csv('원자료옛자료/Z_LHSDW_BLS5_SYS_LAND_CODE.txt',
                         encoding='cp949', sep='|',dtype=str,
                         usecols=['LAD_USE_PLAN_CODE',
                                  'LAD_USE_PLAN_NM',
                                  'CODE_LEVEL',
                                  'USE_AT'])
#print((dictionary['USE_AT'].unique()=='Y').all())
dictionary = dictionary.drop(columns='USE_AT').\
             sort_values(by='CODE_LEVEL',ascending=False).\
             groupby('LAD_USE_PLAN_NM').first()
gdf = gdf.merge(dictionary, left_on='blockType',
                right_index=True, how='left')
#print(gdf['LAD_USE_PLAN_CODE'].isna().any())
#print(gdf['CODE_LEVEL'].value_counts())
gdf = gdf.drop(columns=['CODE_LEVEL']).rename(
    columns={'LAD_USE_PLAN_CODE':'block_type_code',
             'blockName':'block_name'})
'''
gdf['blockNameCode'] = gdf['block_name'].str.replace('[가-힣]','',regex=True)
gdf.loc[gdf['blockType']=='공원','blockNameCode'] = gdf.loc[gdf['blockType']=='공원',
    'block_name'].str.replace('문화?','0',regex=True).str.replace('도','00').\
    str.replace('사','000').str.replace('역','0000').str.replace('공','').values
gdf.loc[gdf['blockType']=='광장','blockNameCode'] = gdf.loc[gdf['blockType']=='광장',
    'block_name'].str.replace('환승','0').str.replace('광','').values
gdf.loc[gdf['blockType']=='산업용지','blockNameCode'] = gdf.loc[gdf['blockType']=='산업용지',
    'block_name'].str.replace('제조','0').str.replace('산업','').values
gdf.loc[gdf['blockType']=='상업용지','blockNameCode'] = gdf.loc[gdf['blockType']=='상업용지',
    'block_name'].str.replace('중상','0').str.replace('일상','00').\
    str.replace('근상','000').values
gdf.loc[gdf['blockType']=='학교','blockNameCode'] = gdf.loc[gdf['blockType']=='학교',
    'block_name'].str.replace('초','0').str.replace('중','00').str.replace('고','000').\
    str.replace('특교','0000').values
'''
gdf[['block_type_code','block_name','geometry']].to_file(
    'ray.gpkg',driver='GPKG',layer='block')

con = sqlite3.connect('ray.gpkg')
cur = con.cursor()
cur.execute('''CREATE TABLE block_type_code_table
(block_type_code TEXT, block_type_name TEXT)''')
cur.executemany('INSERT INTO block_type_code_table VALUES (?, ?)',
                gdf[['block_type_code','blockType']].drop_duplicates().\
                to_records(index=False))
con.commit()
con.close()
