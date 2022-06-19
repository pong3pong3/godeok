import geopandas as gpd
import pandas as pd
from sqlite3 import connect
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
from matplotlib import rcParams
from PIL import Image
con = connect('gd.gpkg')
dictionary = pd.read_sql('SELECT * FROM code',
                         con).set_index('법정동이름').squeeze()
df = pd.read_sql('SELECT * FROM godeok', con)
con.close()
gdf = gpd.read_file('gd.gpkg', layer='map').set_index('land_code')
titles = {'2014': '초기 상태',
          '2015': '평택시 조례\n제1267호',
          '2016': '행정자치부 고시\n제2015-51호',
          '2017': '평택시 고시\n제2017-427호',
          '2018': '국토교통부 고시\n제2019-298호',
          '2019': '평택시 공고\n제2019-2393호',
          '2020': '평택시 공고\n제2020-86호',
          '2021': '평택시 공고\n제2021-3655호',
          '2022': '평택시 공고\n제2022-549호'}
palette = {'서정동':'tab:red','모곡동':'b','지제동':'tab:pink',
           '장당동':'tab:cyan','고덕동':'tab:purple',
           '고덕면 두릉리':'tab:orange','고덕면 여염리':'tab:brown',
           '고덕면 해창리':'tab:blue',
           '고덕면 궁리':'k','고덕면 당현리':'tab:olive',
           '고덕면 방축리':'tab:green',
           '고덕면 율포리':'tab:grey','고덕면 좌교리':'m'}
rcParams['font.family']=['Malgun Gothic']
rcParams['axes.unicode_minus']=False
for year in range(2014,2023):
    year = str(year)
    fig, ax = plt.subplots(figsize=(8,6))
    if year == '2018':
        compete = pd.Index([])
    for i in palette:
        zone = df.loc[df['소재'+year]==i]
        for map_year in (2015, 2021, 2022):
            map_year = str(map_year)
            if year>'2018' and map_year=='2015':
                continue
            tmp = zone.merge(dictionary,
                             left_on='소재'+map_year, right_index=True)
            tmp = (tmp['법정동코드']+tmp['대장구분']+
                   tmp['본번'+map_year] + tmp['부번'+map_year]).unique()
            gdf.loc[gdf.index.isin(tmp)&(gdf['year']==map_year),
                    'geometry'].plot(ax=ax, facecolor=palette[i])
            if year=='2018' and map_year=='2015':
                compete = compete.append(pd.Index(tmp))
    if year=='2018':
        compete = compete[compete.duplicated()].unique()
        gdf.loc[gdf.index.isin(compete), 'geometry'].plot(ax=ax, facecolor='w')
    ax.set_axis_off()
    ax.legend([Patch(facecolor=i) for i in palette.values()],
              palette.keys(),
              bbox_to_anchor=(.95,1))
    ax2 = ax.twiny()
    ax2.set_axis_off()
    ax2.legend(title=titles[year], title_fontsize=16,
               bbox_to_anchor=(.43,.9), frameon=False)
    plt.savefig(year+'.png')
    im = Image.open(year+'.png')
    im.crop((180,70,700,520)).save(year+'.png')
