import pandas as pd
import numpy as np
from scipy.interpolate import RBFInterpolator
import os

# ==== 1. 配置路径（使用 r 确保路径字符串不被转义） ====
INPUT_FILE = r"D:\陈熠辉备份\大三上\寒假科研\ibem_data\data_dahe\light_csv\test_dahe_light_with_laps.csv"
SAVE_DIR = r"D:\陈熠辉备份\大三上\寒假科研\ibem_data\data_dahe\light_csv\environmental field"

# 确保保存文件夹存在
if not os.path.exists(SAVE_DIR):
    os.makedirs(SAVE_DIR)

# 房间尺寸与插值精度（保持你之前的设置）
room_x_min, room_x_max = 0, 138.602
room_y_min, room_y_max = 0, 218.890
x_slice, y_slice = 400, 200

# ==== 2. 读取数据并处理第一圈 ====
df = pd.read_csv(INPUT_FILE)

# 强制转换时间格式，以便提取日期
df['Time'] = pd.to_datetime(df['Time'])

# 提取第一圈（Lap 1）
current_lap = 1
lap_data = df[df['lap'] == current_lap].copy()

if lap_data.empty:
    print(f"错误：在文件中没找到 lap 为 {current_lap} 的数据！")
else:
    # 提取日期字符串 (例如 0916)
    date_str = lap_data['Time'].iloc[0].strftime('%m%d')
    file_name = f"{date_str}_{current_lap}.npz"
    
    # 预处理：剔除 Temp 为 0 的异常行（避免干扰插值）
    lap_data = lap_data[lap_data['Temp'] > 5].reset_index(drop=True)

    # ==== 3. 生成插值网格 ====
    x_slice_j = complex(0, x_slice)
    y_slice_j = complex(0, y_slice)
    xgrid = np.mgrid[room_x_min:room_x_max:x_slice_j, room_y_min:room_y_max:y_slice_j]
    xflat = xgrid.reshape(2, -1).T
    xobs = lap_data[['x', 'y']].values

    # ==== 4. 执行插值计算 ====
    # 定义需要提取的字段
    params = ['Temp', 'Humi', 'Light', 'CO2', 'PM2.5', 'noise']
    field_results = {}

    print(f"正在计算 {date_str} 第 {current_lap} 圈的环境场数据...")

    for p in params:
        if p in lap_data.columns:
            print(f"-> 正在插值: {p}")
            # 使用 RBF 径向基函数进行空间插值
            yflat = RBFInterpolator(xobs, lap_data[p].values)(xflat)
            field_results[p] = yflat.reshape(x_slice, y_slice)

    # ==== 5. 保存结果 ====
    save_path = os.path.join(SAVE_DIR, file_name)
    np.savez_compressed(save_path, **field_results)

    print(f"\n成功！环境场矩阵已保存至: {save_path}")
    print(f"每个矩阵的形状为: {x_slice} x {y_slice}")