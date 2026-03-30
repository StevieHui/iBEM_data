import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import os

# ==== 1. 配置路径 ====
# 指定你要显示的 npz 文件和原始 csv 文件
npz_file = r"D:\陈熠辉备份\大三上\寒假科研\ibem_data\data_daxing\Environmental Field\1224_113.npz"
csv_file = r"D:\陈熠辉备份\大三上\寒假科研\ibem_data\data_daxing\raw_csv\test_daxing.csv"

# 加载插值数据
data = np.load(npz_file)
x_grid = data['x_grid']
y_grid = data['y_grid']
temp_field = data['Temp']

# 加载原始 CSV 提取当前圈的原始点
df = pd.read_csv(csv_file)
# 根据文件名解析出 lap 序号（假设文件名格式是 0103_19.npz）
target_lap = int(os.path.basename(npz_file).split('_')[1].split('.')[0])
raw_points = df[df['lap'] == target_lap]

# ==== 2. 绘图 ====
fig = plt.figure(figsize=(10, 4.2))

# 绘制背景插值场
im = plt.pcolormesh(y_grid, x_grid, temp_field, shading='auto', cmap='rainbow', vmin=16.5, vmax=18.5, alpha=0.8)

# 叠加测点位置（显示成小点点）
# s=2 控制点的大小，c='black' 设置颜色
plt.scatter(raw_points['y'], raw_points['x'], s=2, c='black', label='Sensor Nodes', alpha=0.6)

# 装饰
plt.title(f"Daxing Field & Sensor Points (Lap {target_lap})", fontname='Times New Roman', fontsize=14)
cb = plt.colorbar(im, fraction=0.046, pad=0.04)
cb.set_label('Temperature ($^\circ$C)', fontname='Times New Roman')

plt.axis('off')
plt.legend(loc='upper right', prop={'family': 'Times New Roman', 'size': 10})
plt.tight_layout()

plt.show()