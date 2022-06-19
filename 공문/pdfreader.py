"""
국토교통부고시 제2019-298호의 붙임 1 및
평택시공고 제2015-849호의 참고 2를 csv파일로 변경
"""
import camelot
import pandas as pd

tables = camelot.read_pdf('국토교통부고시제2019-298호(평택고덕국제화계획지구택지개발사업개발계획_8차_및실시계획_6차_변경승인).PDF',
                          pages='12-688')
df = pd.DataFrame()
for i in range(len(tables)):
    df = pd.concat([df,tables[i].df.iloc[1:-1,1:8]])
df.to_csv('../중간자료/국토교통부고시제2019-298호_붙임1.csv',
          index=False,header=False)

tables = camelot.read_pdf('평택시보_제1410호.pdf',
                          pages='19-51')
df = pd.DataFrame()
for i in range(len(tables)):
    df = pd.concat([df,tables[i].df.iloc[1:-1,1:6]])
df.to_csv('../중간자료/평택시공고제2015-849호_참고2.csv',
          index=False,header=False)
