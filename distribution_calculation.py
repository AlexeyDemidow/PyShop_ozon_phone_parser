import pandas as pd

op_s = pd.read_csv('ozon_smartphones/ozon_smartphones/spiders/os_info.csv')

s = op_s['os'].value_counts().reset_index()
for i in range(len(s)):
    print(s.set_index('os').index.tolist()[i] + ' - ' + str(s.set_index('os').values.tolist()[i][0]))
