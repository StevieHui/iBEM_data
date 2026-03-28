import pandas as pd
import numpy as np
from scipy.interpolate import RBFInterpolator
import os

# ==== 1. 配置参数（已按你的要求更新） ====
INPUT_FILE = r"D:\陈熠辉备份\大三上\寒假科研\ibem_data\data_dahe\light_csv\test_dahe_light_with_laps.csv"
SAVE_DIR = r"D:\陈熠辉备份\大三上\寒假科研\ibem_data\data_dahe\light_csv\environmental field"

if not os.path.exists(SAVE_DIR):
    os.makedirs(SAVE_DIR)

# 新的房间尺寸与插值精度
room_x_min, room_x_max = 0, 121.5
room_y_min, room_y_max = 0, 109.5
x_slice, y_slice = 220, 240

# ==== 2. 读取并提取第一圈数据 ====
df = pd.read_csv(INPUT_FILE)
df['Time'] = pd.to_datetime(df['Time'])

current_lap = 1
lap_data = df[df['lap'] == current_lap].copy()

if lap_data.empty:
    print(f"错误：没找到第 {current_lap} 圈数据")
else:
    # 提取日期
    date_str = lap_data['Time'].iloc[0].strftime('%m%d')
    
    # --- 预处理：合并重复坐标点并使用新的 X, Y 列 ---
    # 剔除无效温度点
    lap_data = lap_data[lap_data['Temp'] > 5]
    
    # 针对新的大写 X, Y 进行去重均值化，防止奇异矩阵报错
    print(f"正在处理 {date_str} 第 {current_lap} 圈，合并重复坐标...")
    lap_data = lap_data.groupby(['X', 'Y']).mean(numeric_only=True).reset_index()
    
    # ==== 3. 生成新的插值网格 ====
    # 使用虚数作为步长，确保点数刚好等于 220 和 240
    x_slice_j = complex(0, x_slice)
    y_slice_j = complex(0, y_slice)
    
    # 生成网格坐标 (xgrid[0] 为 X 坐标矩阵, xgrid[1] 为 Y 坐标矩阵)
    xgrid = np.mgrid[room_x_min:room_x_max:x_slice_j, room_y_min:room_y_max:y_slice_j]
    xflat = xgrid.reshape(2, -1).T
    
    # 观测点坐标换成大写的 X, Y
    xobs = lap_data[['X', 'Y']].values

    # ==== 4. 执行插值计算 ====
    # 选取需要保存的环境场参数
    params = ['Temp', 'Humi', 'Light', 'CO2', 'PM2.5', 'noise']
    field_results = {}

    for p in params:
        if p in lap_data.columns:
            print(f"-> 正在计算环境场数据: {p}")
            # RBF插值：使用 thin_plate_spline 核更适合物理场分布
            interp = RBFInterpolator(xobs, lap_data[p].values, kernel='thin_plate_spline')
            yflat = interp(xflat)
            # 还原为 (220, 240) 的矩阵
            field_results[p] = yflat.reshape(x_slice, y_slice)

    # ==== 5. 保存结果（.npz 格式，不画图） ====
    save_path = os.path.join(SAVE_DIR, f"{date_str}_{current_lap}.npz")
    # 同时把网格坐标也存进去，方便之后对位
    np.savez_compressed(save_path, **field_results, grid_x=xgrid[0], grid_y=xgrid[1])

    print(f"\n--- 处理完成 ---")
    print(f"结果已保存为: {save_path}")
    print(f"数据维度: {field_results['Temp'].shape} (X_slice: {x_slice}, Y_slice: {y_slice})")