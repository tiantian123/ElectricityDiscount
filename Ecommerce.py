# -*- coding: utf-8 -*-
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import warnings
warnings.filterwarnings('ignore')

from bokeh.io import output_file
output_file('project04.html')
from bokeh.plotting import figure,show
from bokeh.models import ColumnDataSource

file = 'D:\\0.工作\\数据分析\\【非常重要】课程资料\\CLASSDATA_ch06数据分析项目实战\\练习04_电商打折套路解析\\双十一淘宝美妆数据.xlsx'
# (1)
# 加载数据
data = pd.read_excel(file,index_col=0)
#处理缺失值
data.fillna(0,inplace=True)
# 计算商品总数
ProCount = data['id'].drop_duplicates().count()
# 计算品牌总数
BraCount = data['店名'].drop_duplicates().count()
# 双十一当天在售商品占比情况
Pro_11_ratio = len(data.loc['2016/11/11']) / ProCount

print("**"*40)
print("商品总数为:%d,品牌总数为: %d" % (ProCount,BraCount))
print("双十一当天在售商品占比为：%.2f%%" % (Pro_11_ratio*100))
data['date'] = data.index.day

# 按商品分类，日期聚合
d1 = data[['id','date']].groupby(by='id').agg(['min','max'])['date']
# 标记双十一有在售的商品
id_11 = data[data['date']==11]['id'].unique()
d2 = pd.DataFrame({'id':id_11,'Flag11':True})

data2 = pd.merge(d1,d2,left_index=True,right_on='id',how='left')
data2['Flag11'][data2['Flag11'] != True] = False
'''
③ 按照商品销售节奏分类，我们可以将商品分为7类
   A. 11.11前后及当天都在售 → 一直在售
   B. 11.11之后停止销售 → 双十一后停止销售
   C. 11.11开始销售并当天不停止 → 双十一当天上架并持续在售
   D. 11.11开始销售且当天停止 → 仅双十一当天有售
   E. 11.5 - 11.10 → 双十一前停止销售
   F. 仅11.11当天停止销售 → 仅双十一当天停止销售
   G. 11.12开始销售 → 双十一后上架
'''
data2['type'] = '待分类'
data2['type'][(data2['min']<11)&(data2['max']>11)&(data2['Flag11']==True)] = 'A'
data2['type'][(data2['min']<11)&(data2['max']==11)&(data2['Flag11']==True)] = 'B'
data2['type'][(data2['min']==11)&(data2['max']>11)&(data2['Flag11']==True)] = 'C'
data2['type'][(data2['min']==11)&(data2['max']==11)&(data2['Flag11']==True)] = 'D'
data2['type'][data2['Flag11']==False] = 'F'
data2['type'][(data2['max']<11)&(data2['Flag11']==False)] = 'E'
data2['type'][data2['min']>11] = 'G'

#统计分类情况
result = data2['type'].value_counts()
result = result.loc[['A','B','C','D','E','F','G']]

from bokeh.palettes import brewer
colori = brewer['YlGn'][7]
# 设置调色盘

plt.axis('equal')
plt.pie(result,labels=result.index, autopct="%.2f%%", pctdistance=0.8,
        labeldistance=1.1, startangle=90, radius=1.5, counterclock=False,colors=colori)
plt.savefig('商品分类情况饼图')
plt.show()

'''
未参与双十一当天活动的商品，可能有四种情况：
   con1 → 暂时下架（F）
   con2 → 重新上架（E中部分数据，数据中同一个id可能有不同title，“换个马甲重新上架”），字符串查找特定字符 dataframe.str.contains('预售')
   con3 → 预售（E中部分数据，预售商品的title中包含“预售”二字）
   con4 → 彻底下架（E中部分数据），可忽略
'''
id_not11 = data2[data2['Flag11']==False] # 筛选出双十一当天没参加活动的产品id
print("双十一当天没有参加活动的总商品的个数为: %d,占比为：%.2f%% " %(len(id_not11),len(id_not11)/ProCount*100))
print("双十一当天没参加活动的商品销售节奏类别为：\n", id_not11['type'].value_counts().index.tolist())

# 找到未参加双十一当天活动的商品原始信息
df_not11 = id_not11[['id','type']]
data_not11 = pd.merge(df_not11,data,on='id',how='left')

# 暂时下架数据 con1
id_con1 = data2['id'][data2['type']=='F']

# 修改title后，双十一重新上架 con2
data_con2 = data_not11[['id','title','date']].groupby(by=['id','title']).count()
title_count = data_con2.reset_index()['id'].value_counts()
id_con2 = title_count[title_count>1]

# E中包含预售的商品
data_con3 = data_not11[data_not11['title'].str.contains('预售')]
id_con3 = data_con3['id'].value_counts().index # id 可能存在重复

print("未参与双十一当天活动的商品中：\n暂时下架商品的数量为%i个，重新上架商品的数据量为%i个，预售商品的数据量为%i个" 
      % (len(id_con1), len(id_con2), len(id_con3)))

'''
⑤ 真正参加活动的商品 = 双十一当天在售的商品 + 预售商品 （可以尝试结果去重）
   通过上述几个指标计算，研究出哪些是真正参与双十一活动的品牌，且其商品数量是多
'''
data_11sale = np.hstack((id_11,id_con3)) # 当天在售 + 预售
Pro11Count = len(set(data_11sale))
print('商品总数为%i个' % ProCount)
print('真正参加活动的商品商品总数为%i个，占比为%.2f%%\n-------' % (Pro11Count,Pro11Count/ProCount*100))

# 分别获取双十一当天在售和预售品牌信息
x1 = pd.DataFrame({'id':id_11})
x1_data = pd.merge(x1,data,on='id',how='left')
Brand_11sale = x1_data.groupby(['店名'])['id'].count()

x2 = pd.DataFrame({'id':id_con3})
x2_data = pd.merge(x2,data, on='id', how='left')
Brand_ys = x2_data.groupby('店名')['id'].count()

# 合并双十一在售品牌信息
result = pd.DataFrame({'presale':Brand_ys,'sale_on_11':Brand_11sale})

result['sale11'] = result['sale_on_11'] + result['presale']
sale_on_11 = result['sale_on_11']
result.drop('sale_on_11',axis=1,inplace=True)
result.insert(0,'sale_on_11',sale_on_11)
result.sort_values(by = 'sale11',inplace = True,ascending = False)
#result.columns=['sale_on_11','presale','sale11']

from bokeh.models import HoverTool
from bokeh.core.properties import value
# 导入相关模块

lst_brand = result.index.tolist()
lst_type = result.columns.tolist()[:2]
colors = ['#718dbf','#e84d60']
result.index.name = 'brand'

source = ColumnDataSource(data=result)
# 创建数据

hover = HoverTool(tooltips=[("品牌","@brand"),
                            ("双十一当天在售","@sale_on_11"),
                            ("双十一预售","@presale"),
                            ("参与双十一活动商品总数","@sale11"
                             )]) #设置标签显示内容
p = figure(x_range=lst_brand,plot_width=900,plot_height=350,title="各个品牌参与双十一活动\
           的商品数量分布", tools = [hover,'reset,xwheel_zoom,pan,crosshair'])
# 构建绘图空间
p.vbar_stack(lst_type,
             x='brand',
             source=source,
             width=0.9,color=colors,alpha=0.8,legend=[value(x) for x in lst_type],
             muted_color='black',muted_alpha=0.2
             )
# 绘制堆叠图
p.xgrid.grid_line_color = None
p.axis.minor_tick_line_color = None
p.outline_line_color = None
p.legend.location = 'top_right'
p.legend.orientation = 'horizontal'
p.legend.click_policy='mute'
# 设置其他参数
show(p)
