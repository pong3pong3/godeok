import geopandas as gpd
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
from matplotlib import rcParams
from PIL import Image
gdf = gpd.read_file('gaori.gpkg')
palette = {'고덕동':'b','고덕면 율포리':'b','고덕면 좌교리':'m',
           '고덕면 여염리':'tab:orange','고덕면 방축리':'tab:brown',
           '고덕면 동고리':'tab:pink','고덕면 궁리':'tab:blue',
           '고덕면 해창리':'k','고덕면 동청리':'tab:olive',
           '고덕면 문곡리':'tab:purple','고덕면 두릉리':'tab:green',
           '고덕면 당현리':'tab:grey','서정동':'tab:red',
           '장당동':'tab:cyan', '신대동':'aqua',
           '서탄면 황구지리':'lime', '서탄면 장등리':'lime'}
rcParams['font.family']=['Malgun Gothic']
rcParams['axes.unicode_minus']=False
rcParams['hatch.linewidth'] = 0.3
for year in range(2015,2023):
    year = str(year)
    fig, ax = plt.subplots(figsize=(6,5))
    for i in palette:
        gdf.loc[gdf[year+'_소재']==i,'geometry'].plot(ax=ax,
                                                    facecolor=palette[i])
    gdf.loc[gdf[year+'_소재'].isna(),'geometry'].plot(ax=ax,
                                                    hatch='/'*5,
                                                    facecolor='w')
    ax.legend([Patch(facecolor=i) for i in palette.values()],
              palette.keys(),
              bbox_to_anchor=(1.55,1))
    ax.set_axis_off()
    plt.savefig(year+'.png')
    im = Image.open(year+'.png')
    im.crop((150,50,600,450)).save(year+'.png')
