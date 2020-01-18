# -*- coding: utf-8 -*-
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import warnings
warnings.filterwarnings('ignore')

from bokeh.plotting import figure,show,output_file
from bokeh.models import ColumnDataSource,HoverTool

# (1) 加载数据
file = 'D:\\0.工作\\数据分析\\【非常重要】课程资料\\CLASSDATA_ch06数据分析项目实战\\练习04_电商打折套路解析\\双十一淘宝美妆数据.xlsx'
data = pd.read_excel(file,index_col=0)
data.fillna(0,inplace=True)
data.index.name = 'update_time'
data['date'] = data.index.day

data2 = data
data2['period'] = pd.cut(data2['date'],[4,10,11,14],labels=['双十一之前','双十一','双十一后'])
# 筛选数据
'''
(2) 针对每个商品，评估其打折的情况
'''
price = data2[['id','price','period']].groupby(['id','price']).min()
price.reset_index(inplace=True)
# 查看数据是否有波动

id_count = price['id'].value_counts()
id_type1 = id_count[id_count==1].index
id_type2 = id_count[id_count != 1].index
# 筛选出打折与不打折的数据

'''
(3) 针对打折的商品，其折扣率是多少
'''
result2 = data2[['id','price','period','店名']].groupby(['id','price']).min()
result2.reset_index(inplace=True)
result_before = result2[result2['period']=='双十一之前']
result_at11 = result2[result2['period'] == '双十一']
result_data2 = pd.merge(result_before,result_at11,on='id')
# 合并数据

result_data2['zkl'] = result_data2['price_y'] /result_data2['price_x']
# 计算折扣率

bokeh_data = result_data2[['id','zkl']].dropna()
bokeh_data['zkl_range'] = pd.cut(bokeh_data['zkl'],bins=np.linspace(0,1,21)).astype(str)
bokeh_data2 = bokeh_data.groupby('zkl_range').count().iloc[:-1]
#bokeh_data2.index.name = 'range'
#bokeh_data2.index = bokeh_data2.index.astype(np.str)
bokeh_data2['zkl_pre'] = bokeh_data2['zkl']/bokeh_data2['zkl'].sum()
# 计算折扣区间
output_file('project040_h2.html')
source1 = ColumnDataSource(bokeh_data2)
#lst_zkl = bokeh_data2['zkl_range'].tolist()
lst_zkl = bokeh_data2.index.tolist()
#lst_zkl = [str(x) for x in lst_zkl]
hover = HoverTool(tooltips=[('折扣率',"@zkl")])

p = figure(x_range=lst_zkl,plot_width=900,plot_height=350,title="商品折扣率统计",
           tools=[hover,'reset,xwheel_zoom,pan,crosshair'])

p.line(x='zkl_range',y='zkl_pre',source=source1,
       line_color='black',line_dash=[10,4])
p.circle(x='zkl_range',y='zkl_pre',source=source1,
         size=8,color='red',alpha=0.6)
show(p)

'''
(4) 按照品牌分析， 不同品牌的折扣力度
'''
from bokeh.transform import jitter
brand = result_data2['店名_x'].dropna().unique().tolist()
bokeh_data3 = result_data2[['id','zkl','店名_x']].dropna()
bokeh_data3= bokeh_data3[bokeh_data3['zkl']<0.96]
source2 = ColumnDataSource(bokeh_data3)

output_file('prject04_pic3.html')
p2 = figure(y_range=brand,plot_width=900,plot_height=500,title='不同品牌的折扣率情况',
            tools=[hover,'box_select,reset,xwheel_zoom,pan,crosshair'])
p2.circle(x = 'zkl',
          y= jitter('店名_x',width=0.5,range=p2.y_range),
          source = source2, alpha=0.3)
show(p2)







