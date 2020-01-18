# -*- coding: utf-8 -*-
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import warnings
warnings.filterwarnings('ignore')

from bokeh.plotting import figure,show,output_file
from bokeh.models import ColumnDataSource
from bokeh.models import HoverTool

from bokeh.models.annotations import Span
from bokeh.models.annotations import Label
from bokeh.models.annotations import BoxAnnotation


'''
(1) 数据计算
'''
data_zk = result_data2[result_data2['zkl']<0.95]
result_zkld = data_zk.groupby('店名_y')['zkl'].mean()

n_dz = data_zk['店名_y'].value_counts()
n_zs = result_data2['店名_y'].value_counts()

result_dzspbl = pd.DataFrame({'打折商品数':n_dz,'商品总数':n_zs})
result_dzspbl['参与打折商品比例'] = result_dzspbl['打折商品数']/result_dzspbl['商品总数']
result_dzspbl.dropna(inplace=True)

result_sum = result.copy()
# 筛选出品牌参加双十一活动的总数

result_data4 = pd.merge(pd.DataFrame(result_zkld),result_dzspbl,left_index=True,right_index=True,how='inner')
result_data4 = pd.merge(result_data4,result_sum,left_index=True,right_index=True,how='inner')
# 合并数据
bokeh_data4 = result_data4[['zkl','sale11','参与打折商品比例']]
bokeh_data4.columns = ['zkl','count','ratio']
bokeh_data4['size'] = bokeh_data4['count']*0.03

source4 = ColumnDataSource(bokeh_data4)

hover = HoverTool(tooltips=[("品牌","@index"),
                            ("折扣率","@zkl"),
                            ("商品总数","@count"),
                            ("参与打折商品比例","@ratio")])
output_file("project04_pic4.html")
p = figure(plot_width=600,plot_height=600,
           title="各个商品打折套路解析",
           tools=[hover,'box_select,reset,wheel_zoom,pan,crosshair'])
# 构建绘图空间
p.circle_x(x='ratio',y='zkl',source=source4,size='size',
           fill_color='red',line_color='black',fill_alpha=0.6,line_dash=[8,3])
p.ygrid.grid_line_dash =[6,4]
p.xgrid.grid_line_dash = [6,4]
# 散点图
x_mean = bokeh_data4['ratio'].mean()
y_mean = bokeh_data4['zkl'].mean()

# 绘制辅助线
x = Span(location=x_mean,dimension="height",line_color='green',line_alpha=0.7,line_width=1.5,line_dash=[6,4])
y = Span(location=y_mean,dimension='width',line_color='green',line_alpha=0.7,line_width=1.5,line_dash=[6,4])
p.add_layout(x)
p.add_layout(y)
# 绘制辅助线

bg1 = BoxAnnotation(bottom=y_mean, right=x_mean,fill_alpha=0.1, fill_color='olive')
label1 = Label(x=0.1, y=0.55,text="少量大打折",text_font_size="10pt" )
p.add_layout(bg1)
p.add_layout(label1)
# 绘制第一象限

bg2 = BoxAnnotation(bottom=y_mean, left=x_mean, fill_alpha=0.1, fill_color='firebrick')
label2 = Label(x=0.7, y=0.55, text='大量大打折', text_font_size='10pt')
p.add_layout(bg2)
p.add_layout(label2)
# 绘制第二象限
bg3 = BoxAnnotation(top=y_mean, right=x_mean, fill_alpha=0.1, fill_color='firebrick')
label3 = Label(x=0.1, y=0.8, text='少量少打折', text_font_size='10pt')
p.add_layout(bg3)
p.add_layout(label3)
# 绘制第三象限

bg4 = BoxAnnotation(top=y_mean, right=x_mean, fill_alpha=0.1, fill_color='firebrick')
label4 = Label(x=0.7, y=0.8, text='大量少打折', text_font_size='10pt')
p.add_layout(bg4)
p.add_layout(label4)
# 绘制第四象限

show(p)
