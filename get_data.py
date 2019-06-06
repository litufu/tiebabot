import pandas as pd
from sqlalchemy import create_engine

engine = create_engine('sqlite:///tiebar.sqlite')
con = engine.connect()#创建连接

# 添加数据
# df = pd.read_csv('./university.csv',names=['name'])
# df = df[["name"]]
# df.to_sql(name='daxue', con=con, if_exists='append', index=False)

# print(df[:5])

df1 = pd.read_sql_table('gaozhong',con)
# print(df1[:5])
for school_name in list(df1[:5]["school_name"]):
    print(school_name)
