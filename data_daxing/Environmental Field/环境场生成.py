import pandas as pd
import numpy as np
from scipy.interpolate import RBFInterpolator
import matplotlib.pyplot as plt
import os
from matplotlib.ticker import FormatStrFormatter


### 参数集中输入 ###
### 房间尺寸（外接矩形） ###
room_x_min = 0
room_x_max = 80.105
room_y_min = 0
room_y_max = 168.353

### x,y方向的插值份数 ###
x_slice = 400
y_slice = 200

### 待处理的日期+圈数 ###
date = '0103'
lap = '19'
lap_num = date + '-' + lap


### 读入传感器数据 ###
file_name_1 = 'data_processed/' + lap_num + '.csv'
#file_name_1 = 'data_processed/0104暂存/' + lap_num + '.csv'
data_1 = pd.read_csv(file_name_1)

data_1 = data_1.loc[(data_1['Temp']!=0)]#删除零行
data_1_index=data_1.loc[:,'Humi'] # loc取列必须:,列名；取行则直接行名即可

data_1 = data_1.reset_index(drop=True)

# 环境参数修正
for i in range(0,len(data_1)):
    data_1.loc[i,'Temp'] = data_1.loc[i,'Temp'] + 0.49
    data_1.loc[i,'Humi'] = data_1.loc[i,'Humi'] - 1.15
    data_1.loc[i,'Light'] = data_1.loc[i,'Light'] - 80
    data_1.loc[i,'CO2'] = data_1.loc[i,'CO2'] - 369.34
    data_1.loc[i,'PM2.5'] = data_1.loc[i,'PM2.5'] - 0.69


### 空间插值 ###
#待插值传参
x = data_1.loc[:,"x"]#x坐标
y = data_1.loc[:,"y"]#y坐标
T = data_1.loc[:,"Temp"]#温度
#T = data_5
H = data_1.loc[:,"Humi"]#湿度
L = data_1.loc[:,"Light"]#照度不要固定点
C = data_1.loc[:,"CO2"]#二氧化碳
PM = data_1.loc[:,"PM2.5"]#PM2.5
N = data_1.loc[:,"noise"]#噪声

xobs = np.zeros((x.shape[0],2))
for i in range(x.shape[0]):
    xobs[i,0]=x[i]
    xobs[i,1]=y[i]


#插值后坐标点生成
x_slice_j = complex(0,x_slice)#用切片份数作为虚部生成复数，后面mgrid中用到
y_slice_j = complex(0,y_slice)
xgrid = np.mgrid[room_x_min:room_x_max:x_slice_j,room_y_min:room_y_max:y_slice_j]#步长用复数表示点数
x1,y1 = np.mgrid[room_x_min:room_x_max:x_slice_j,room_y_min:room_y_max:y_slice_j]


#RBF插值
xflat = xgrid.reshape(2,-1).T
#温度插值
yflat_T = RBFInterpolator(xobs,T)(xflat)
yflat_T = yflat_T.reshape(x_slice,y_slice)
#湿度插值
yflat_H = RBFInterpolator(xobs,H)(xflat)
yflat_H = yflat_H.reshape(x_slice,y_slice)
#照度插值
yflat_L = RBFInterpolator(xobs,L)(xflat)
yflat_L = yflat_L.reshape(x_slice,y_slice)
#二氧化碳插值
yflat_C = RBFInterpolator(xobs,C)(xflat)
yflat_C = yflat_C.reshape(x_slice,y_slice)
#PM2.5插值
yflat_PM = RBFInterpolator(xobs,PM)(xflat)
yflat_PM = yflat_PM.reshape(x_slice,y_slice)
#噪声插值
yflat_N = RBFInterpolator(xobs,N)(xflat)
yflat_N = yflat_N.reshape(x_slice,y_slice)
#各个yflat均为200*200与插值后坐标的尺寸一致


# ### 画图 ###
# fig = plt.figure(figsize=(10, 4.2))  # 设置画布大小

# # 图1绘制温度场
# # im = plt.pcolormesh(y1, x1, yflat_T, shading='auto', cmap='rainbow', vmin=17.5, vmax=19.5)
# # im = plt.pcolormesh(y1, x1, yflat_T, shading='auto', cmap='rainbow', vmin=14, vmax=20)
# im = plt.pcolormesh(y1, x1, yflat_T, shading='auto', cmap='rainbow', vmin=16.5, vmax=18.5)
# # im = plt.pcolormesh(y1, x1, yflat_T, shading='auto', cmap='rainbow', vmin=18.5, vmax=19.5)
# # im_points = plt.plot(y, x, "x", c='black', label="input point")  # 标出测点位置
# im_points = plt.plot(y, x, "^", c='red', label="input point",markeredgecolor='black')  # 标出测点位置
# # cd = plt.colorbar(im, ticks=np.linspace(17.5, 19.5, 5), orientation='vertical', pad=0.05)  # pad控制间距
# # cd = plt.colorbar(im, ticks=np.linspace(14, 20, 7), orientation='vertical', pad=0.05)  # pad控制间距
# cd = plt.colorbar(im, ticks=np.linspace(16.5, 18.5, 5), orientation='vertical', pad=0.05)  # pad控制间距
# cd.set_label('Temperature ($^\circ$C)', size=15, rotation=90, fontname='Times New Roman')  # 色阶标签竖直显示
# cd.ax.yaxis.set_major_formatter(FormatStrFormatter('%.1f'))
# cd.ax.tick_params(labelsize=12)  # 设置刻度字号
# for t in cd.ax.get_yticklabels():  # 遍历 colorbar 刻度标签
#     t.set_fontname('Times New Roman')

# plt.axis('off')  # 关闭坐标轴
# plt.tight_layout()  # 调整布局以避免重叠
# # plt.savefig('./pic/临时/Temp_' + date + '_' + lap + '.png', dpi=300, bbox_inches='tight')  # 保存为PNG格式，分辨率300dpi，自动调整边界
# plt.savefig('./pic/不同路径环境场对比/Temp/Temp_' + date + '_' + lap + '.png', dpi=300, bbox_inches='tight')  # 保存为PNG格式，分辨率300dpi，自动调整边界
# #plt.show()


# # ### 画图 ###
# # fig2 = plt.figure(figsize=(10, 4.2))  # 设置画布大小

# # # 图2绘制光环境场
# # im2 = plt.pcolormesh(y1, x1, yflat_L, shading='auto', cmap='rainbow', vmin=0, vmax=700)
# # im2_points = plt.plot(y, x, "x", c='black', label="input point")  # 标出测点位置
# # cd2 = plt.colorbar(im2, ticks=np.linspace(0, 700, 8), orientation='vertical')  # pad控制间距
# # cd2.set_label('Illuminance (lx)', size=15, rotation=90, fontname='Times New Roman')  # 色阶标签竖直显示
# # cd2.ax.yaxis.set_major_formatter(FormatStrFormatter('%d'))
# # cd2.ax.tick_params(labelsize=12)  # 设置刻度字号
# # for t in cd2.ax.get_yticklabels():  # 遍历 colorbar 刻度标签
# #     t.set_fontname('Times New Roman')

# # plt.axis('off')  # 关闭坐标轴
# # plt.tight_layout()  # 调整布局以避免重叠
# # #plt.savefig('./pic/临时/Light_' + date + '_' + lap + '.png', dpi=300, bbox_inches='tight')  # 保存为PNG格式，分辨率300dpi，自动调整边界
# # #plt.show()



# ### 画图 ###
# fig3 = plt.figure(figsize=(10, 4.2))  # 设置画布大小

# # 图3绘制CO2场
# #im3 = plt.pcolormesh(y1, x1, yflat_C, shading='auto', cmap='rainbow', vmin=500, vmax=1000)
# # im3 = plt.pcolormesh(y1, x1, yflat_C, shading='auto', cmap='rainbow', vmin=800, vmax=900)
# im3 = plt.pcolormesh(y1, x1, yflat_C, shading='auto', cmap='rainbow', vmin=400, vmax=600)
# # im3_points = plt.plot(y, x, "x", c='black', label="input point")  # 标出测点位置
# im3_points = plt.plot(y, x, "^", c='red', label="input point",markeredgecolor='black')  # 标出测点位置
# # cd3 = plt.colorbar(im3, ticks=np.linspace(500, 1000, 6), orientation='vertical')  # pad控制间距
# # cd3 = plt.colorbar(im3, ticks=np.linspace(800, 900, 5), orientation='vertical')  # pad控制间距
# cd3 = plt.colorbar(im3, ticks=np.linspace(400, 600, 5), orientation='vertical')  # pad控制间距
# cd3.set_label('CO2 (ppm)', size=15, rotation=90, fontname='Times New Roman')  # 色阶标签竖直显示
# cd3.ax.yaxis.set_major_formatter(FormatStrFormatter('%d'))
# cd3.ax.tick_params(labelsize=12)  # 设置刻度字号
# for t in cd3.ax.get_yticklabels():  # 遍历 colorbar 刻度标签
#     t.set_fontname('Times New Roman')

# plt.axis('off')  # 关闭坐标轴
# plt.tight_layout()  # 调整布局以避免重叠
# #plt.savefig('./pic/临时/CO2_' + date + '_' + lap + '.png', dpi=300, bbox_inches='tight')  # 保存为PNG格式，分辨率300dpi，自动调整边界
# plt.savefig('./pic/不同路径环境场对比/CO2/CO2_' + date + '_' + lap + '.png', dpi=300, bbox_inches='tight')  # 保存为PNG格式，分辨率300dpi，自动调整边界
# #plt.show()



### 画图 ###
fig4 = plt.figure(figsize=(10, 4.2))  # 设置画布大小

# 图4绘制PM2.5场
# im4 = plt.pcolormesh(y1, x1, yflat_PM, shading='auto', cmap='rainbow', vmin=35, vmax=75)
# im4 = plt.pcolormesh(y1, x1, yflat_PM, shading='auto', cmap='rainbow', vmin=15, vmax=45)
im4 = plt.pcolormesh(y1, x1, yflat_PM, shading='auto', cmap='rainbow', vmin= 15, vmax= 45)
im4_points = plt.plot(y, x, "x", c='black', label="input point")  # 标出测点位置
# im4_points = plt.plot(y, x, "^", c='red', label="input point",markeredgecolor='black')  # 标出测点位置
# cd4 = plt.colorbar(im4, ticks=np.linspace(35, 75, 5), orientation='vertical')  # pad控制间距
# cd4 = plt.colorbar(im4, ticks=np.linspace(15, 45, 4), orientation='vertical')  # pad控制间距
cd4 = plt.colorbar(im4, ticks=np.linspace(15, 45, 7), orientation='vertical')  # pad控制间距
cd4.set_label(r'PM2.5 ($\mu$g/m3)', size=15, rotation=90, fontname='Times New Roman')  # 色阶标签竖直显示
cd4.ax.yaxis.set_major_formatter(FormatStrFormatter('%d'))
cd4.ax.tick_params(labelsize=12)  # 设置刻度字号
for t in cd4.ax.get_yticklabels():  # 遍历 colorbar 刻度标签
    t.set_fontname('Times New Roman')

plt.axis('off')  # 关闭坐标轴
plt.tight_layout()  # 调整布局以避免重叠
#plt.savefig('./pic/临时/PM25_' + date + '_' + lap + '.png', dpi=300, bbox_inches='tight')  # 保存为PNG格式，分辨率300dpi，自动调整边界
plt.savefig('./pic/不同路径环境场对比/PM2.5/PM25_' + date + '_' + lap + '.png', dpi=300, bbox_inches='tight')  # 保存为PNG格式，分辨率300dpi，自动调整边界
#plt.show()




# ### 画图 ###
# fig5 = plt.figure(figsize=(10, 4.2))  # 设置画布大小

# # 图5绘制噪声场
# # im5 = plt.pcolormesh(y1, x1, yflat_N, shading='auto', cmap='rainbow', vmin=45, vmax=65)
# im5 = plt.pcolormesh(y1, x1, yflat_N, shading='auto', cmap='rainbow', vmin=70, vmax=80)
# im5_points = plt.plot(y, x, "x", c='black', label="input point")  # 标出测点位置
# # cd5 = plt.colorbar(im5, ticks=np.linspace(45, 65, 5), orientation='vertical')  # pad控制间距
# cd5 = plt.colorbar(im5, ticks=np.linspace(70, 80, 5), orientation='vertical')  # pad控制间距
# cd5.set_label('Noise (dB)', size=15, rotation=90, fontname='Times New Roman')  # 色阶标签竖直显示
# cd5.ax.yaxis.set_major_formatter(FormatStrFormatter('%d'))
# cd5.ax.tick_params(labelsize=12)  # 设置刻度字号
# for t in cd5.ax.get_yticklabels():  # 遍历 colorbar 刻度标签
#     t.set_fontname('Times New Roman')

# plt.axis('off')  # 关闭坐标轴
# plt.tight_layout()  # 调整布局以避免重叠
# #plt.savefig('./pic/临时/Noise_' + date + '_' + lap + '.png', dpi=300, bbox_inches='tight')  # 保存为PNG格式，分辨率300dpi，自动调整边界
# #plt.show()









# ### 画图 ###
# fig = plt.figure(figsize=(10, 4.2))  # 设置画布大小

# # 图1绘制温度场
# # im = plt.pcolormesh(y1, x1, yflat_T, shading='auto', cmap='rainbow', vmin=17.5, vmax=19.5)
# im = plt.pcolormesh(y1, x1, yflat_T, shading='auto', cmap='rainbow', vmin=19.5, vmax=21.5)
# im_points = plt.plot(y, x, "x", c='black', label="input point")  # 标出测点位置
# # cd = plt.colorbar(im, ticks=np.linspace(17.5, 19.5, 5), orientation='vertical', pad=0.05)  # pad控制间距
# cd = plt.colorbar(im, ticks=np.linspace(19.5, 21.5, 5), orientation='vertical', pad=0.05)  # pad控制间距
# cd.set_label('Temperature ($^\circ$C)', size=15, rotation=90, fontname='Times New Roman')  # 色阶标签竖直显示
# cd.ax.yaxis.set_major_formatter(FormatStrFormatter('%.1f'))
# cd.ax.tick_params(labelsize=12)  # 设置刻度字号
# for t in cd.ax.get_yticklabels():  # 遍历 colorbar 刻度标签
#     t.set_fontname('Times New Roman')

# plt.axis('off')  # 关闭坐标轴
# plt.tight_layout()  # 调整布局以避免重叠
# plt.savefig('./pic/Temp/Temp_' + date + '_' + lap + '.png', dpi=300, bbox_inches='tight')  # 保存为PNG格式，分辨率300dpi，自动调整边界
# #plt.show()


# ### 画图 ###
# fig2 = plt.figure(figsize=(10, 4.2))  # 设置画布大小

# # 图2绘制光环境场
# im2 = plt.pcolormesh(y1, x1, yflat_L, shading='auto', cmap='rainbow', vmin=0, vmax=500)
# im2_points = plt.plot(y, x, "x", c='black', label="input point")  # 标出测点位置
# cd2 = plt.colorbar(im2, ticks=np.linspace(0, 500, 6), orientation='vertical')  # pad控制间距
# cd2.set_label('Illuminance (lx)', size=15, rotation=90, fontname='Times New Roman')  # 色阶标签竖直显示
# cd2.ax.yaxis.set_major_formatter(FormatStrFormatter('%d'))
# cd2.ax.tick_params(labelsize=12)  # 设置刻度字号
# for t in cd2.ax.get_yticklabels():  # 遍历 colorbar 刻度标签
#     t.set_fontname('Times New Roman')

# plt.axis('off')  # 关闭坐标轴
# plt.tight_layout()  # 调整布局以避免重叠
# plt.savefig('./pic/Light/Light_' + date + '_' + lap + '.png', dpi=300, bbox_inches='tight')  # 保存为PNG格式，分辨率300dpi，自动调整边界
# #plt.show()



# ### 画图 ###
# fig3 = plt.figure(figsize=(10, 4.2))  # 设置画布大小

# # 图3绘制CO2场
# #im3 = plt.pcolormesh(y1, x1, yflat_C, shading='auto', cmap='rainbow', vmin=500, vmax=1000)
# # im3 = plt.pcolormesh(y1, x1, yflat_C, shading='auto', cmap='rainbow', vmin=800, vmax=900)
# im3 = plt.pcolormesh(y1, x1, yflat_C, shading='auto', cmap='rainbow', vmin=400, vmax=550)
# im3_points = plt.plot(y, x, "x", c='black', label="input point")  # 标出测点位置
# # cd3 = plt.colorbar(im3, ticks=np.linspace(500, 1000, 6), orientation='vertical')  # pad控制间距
# # cd3 = plt.colorbar(im3, ticks=np.linspace(800, 900, 5), orientation='vertical')  # pad控制间距
# cd3 = plt.colorbar(im3, ticks=np.linspace(400, 550, 4), orientation='vertical')  # pad控制间距
# cd3.set_label('CO2 (ppm)', size=15, rotation=90, fontname='Times New Roman')  # 色阶标签竖直显示
# cd3.ax.yaxis.set_major_formatter(FormatStrFormatter('%d'))
# cd3.ax.tick_params(labelsize=12)  # 设置刻度字号
# for t in cd3.ax.get_yticklabels():  # 遍历 colorbar 刻度标签
#     t.set_fontname('Times New Roman')

# plt.axis('off')  # 关闭坐标轴
# plt.tight_layout()  # 调整布局以避免重叠
# plt.savefig('./pic/CO2/CO2_' + date + '_' + lap + '.png', dpi=300, bbox_inches='tight')  # 保存为PNG格式，分辨率300dpi，自动调整边界
# #plt.show()



# ### 画图 ###
# fig4 = plt.figure(figsize=(10, 4.2))  # 设置画布大小

# # 图4绘制PM2.5场
# # im4 = plt.pcolormesh(y1, x1, yflat_PM, shading='auto', cmap='rainbow', vmin=35, vmax=75)
# # im4 = plt.pcolormesh(y1, x1, yflat_PM, shading='auto', cmap='rainbow', vmin=15, vmax=45)
# im4 = plt.pcolormesh(y1, x1, yflat_PM, shading='auto', cmap='rainbow', vmin= 15, vmax= 55)
# im4_points = plt.plot(y, x, "x", c='black', label="input point")  # 标出测点位置
# # cd4 = plt.colorbar(im4, ticks=np.linspace(35, 75, 5), orientation='vertical')  # pad控制间距
# # cd4 = plt.colorbar(im4, ticks=np.linspace(15, 45, 4), orientation='vertical')  # pad控制间距
# cd4 = plt.colorbar(im4, ticks=np.linspace(15, 55, 5), orientation='vertical')  # pad控制间距
# cd4.set_label(r'PM2.5 ($\mu$g/m3)', size=15, rotation=90, fontname='Times New Roman')  # 色阶标签竖直显示
# cd4.ax.yaxis.set_major_formatter(FormatStrFormatter('%d'))
# cd4.ax.tick_params(labelsize=12)  # 设置刻度字号
# for t in cd4.ax.get_yticklabels():  # 遍历 colorbar 刻度标签
#     t.set_fontname('Times New Roman')

# plt.axis('off')  # 关闭坐标轴
# plt.tight_layout()  # 调整布局以避免重叠
# plt.savefig('./pic/PM25/PM25_' + date + '_' + lap + '.png', dpi=300, bbox_inches='tight')  # 保存为PNG格式，分辨率300dpi，自动调整边界
# #plt.show()




# ### 画图 ###
# fig5 = plt.figure(figsize=(10, 4.2))  # 设置画布大小

# # 图5绘制噪声场
# # im5 = plt.pcolormesh(y1, x1, yflat_N, shading='auto', cmap='rainbow', vmin=45, vmax=65)
# im5 = plt.pcolormesh(y1, x1, yflat_N, shading='auto', cmap='rainbow', vmin=70, vmax=80)
# im5_points = plt.plot(y, x, "x", c='black', label="input point")  # 标出测点位置
# # cd5 = plt.colorbar(im5, ticks=np.linspace(45, 65, 5), orientation='vertical')  # pad控制间距
# cd5 = plt.colorbar(im5, ticks=np.linspace(70, 80, 5), orientation='vertical')  # pad控制间距
# cd5.set_label('Noise (dB)', size=15, rotation=90, fontname='Times New Roman')  # 色阶标签竖直显示
# cd5.ax.yaxis.set_major_formatter(FormatStrFormatter('%d'))
# cd5.ax.tick_params(labelsize=12)  # 设置刻度字号
# for t in cd5.ax.get_yticklabels():  # 遍历 colorbar 刻度标签
#     t.set_fontname('Times New Roman')

# plt.axis('off')  # 关闭坐标轴
# plt.tight_layout()  # 调整布局以避免重叠
# plt.savefig('./pic/Noise/Noise_' + date + '_' + lap + '.png', dpi=300, bbox_inches='tight')  # 保存为PNG格式，分辨率300dpi，自动调整边界
# plt.show()