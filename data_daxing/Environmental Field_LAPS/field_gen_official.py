import pandas as pd
import numpy as np
from scipy.interpolate import RBFInterpolator
import os

# ==== 1. 参数集中输入 ====
room_x_min, room_x_max = 0, 80.105
room_y_min, room_y_max = 0, 168.353
x_slice, y_slice = 400, 200

input_file = r"D:\陈熠辉备份\大三上\寒假科研\ibem_data\data_daxing\raw_csv\test_daxing.csv"
output_dir = r"D:\陈熠辉备份\大三上\寒假科研\ibem_data\data_daxing\Environmental Field"

if not os.path.exists(output_dir):
    os.makedirs(output_dir)

# ==== 2. 读取数据 ====
df = pd.read_csv(input_file)
df['Time'] = pd.to_datetime(df['Time'])
df['date_str'] = df['Time'].dt.strftime('%m%d')

# 获取所有圈数
laps = df['lap'].unique()

# ==== 3. 循环处理并生成 NPZ ====
for lap in laps:
    data_lap = df[df['lap'] == lap].copy()
    if data_lap.empty: continue
    
    date = data_lap['date_str'].iloc[0]
    file_name = f"{date}_{lap}.npz"
    print(f"正在生成数据文件: {file_name}")

    # 准备插值点 (大兴坐标 X2, Y2)
    x_obs = data_lap[['x', 'y']].values
    
    # 待处理参数列表
    params_to_interp = {
        'Temp': data_lap['Temp'],
        'Humi': data_lap['Humi'],
        'Light': data_lap['Light'],
        'CO2': data_lap['CO2'],
        'PM25': data_lap['PM2.5'],
        'Noise': data_lap['noise']
    }

    # 生成网格坐标 (与你之前的 y1, x1 逻辑一致)
    x_slice_j = complex(0, x_slice)
    y_slice_j = complex(0, y_slice)
    x_grid, y_grid = np.mgrid[room_x_min:room_x_max:x_slice_j, room_y_min:room_y_max:y_slice_j]
    grid_flat = np.vstack([x_grid.ravel(), y_grid.ravel()]).T

    # 存储插值结果的字典
    save_dict = {
        'x_grid': x_grid,
        'y_grid': y_grid
    }

    for p_name, p_val in params_to_interp.items():
        try:
            # RBF 插值并还原形状
            interp_res = RBFInterpolator(x_obs, p_val)(grid_flat)
            save_dict[p_name] = interp_res.reshape(x_slice, y_slice)
        except:
            print(f"  [警告] {p_name} 插值失败，跳过。")

    # ==== 4. 保存为 NPZ ====
    save_path = os.path.join(output_dir, file_name)
    np.savez_compressed(save_path, **save_dict)

print(f"\n全部处理完毕！NPZ 文件已存至: {output_dir}")