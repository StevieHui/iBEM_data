import pandas as pd
import numpy as np
from scipy.interpolate import RBFInterpolator
import os
import warnings

# 忽略 RBF 可能产生的微小数值警告
warnings.filterwarnings("ignore")

# ==== 1. 配置参数 ====
INPUT_FILE = r"D:\陈熠辉备份\大三上\寒假科研\ibem_data\data_dahe\light_csv\test_dahe_light_with_laps.csv"
SAVE_DIR = r"D:\陈熠辉备份\大三上\寒假科研\ibem_data\data_dahe\light_csv\environmental field"

if not os.path.exists(SAVE_DIR):
    os.makedirs(SAVE_DIR)

# 房间尺寸与插值精度
room_x_min, room_x_max = 0, 121.5
room_y_min, room_y_max = 0, 109.5
x_slice, y_slice = 220, 240

# ==== 2. 读取数据 ====
print("正在读取原始数据...")
df = pd.read_csv(INPUT_FILE)
df['Time'] = pd.to_datetime(df['Time'])

# 获取所有不重复的圈数编号
all_laps = sorted(df['lap'].unique())
print(f"检测到共 {len(all_laps)} 圈数据，准备开始批量生成...")

# ==== 3. 准备插值网格 ====
x_slice_j = complex(0, x_slice)
y_slice_j = complex(0, y_slice)
xgrid = np.mgrid[room_x_min:room_x_max:x_slice_j, room_y_min:room_y_max:y_slice_j]
xflat = xgrid.reshape(2, -1).T

# ==== 4. 循环处理每一圈 ====
params = ['Temp', 'Humi', 'Light', 'CO2', 'PM2.5', 'noise']

for lap_id in all_laps:
    # 提取当前圈数据
    lap_data = df[df['lap'] == lap_id].copy()
    
    # 跳过数据量太少的无效圈（RBF 至少需要几个点才能工作）
    if len(lap_data) < 10:
        continue
        
    # 提取日期
    date_str = lap_data['Time'].iloc[0].strftime('%m%d')
    file_name = f"{date_str}_{lap_id}.npz"
    save_path = os.path.join(SAVE_DIR, file_name)
    
    # 检查是否已经生成过，避免重复跑
    if os.path.exists(save_path):
        print(f"跳过: {file_name} (已存在)")
        continue

    print(f"正在处理: {file_name} ...", end='\r')

    # 数据预处理：去重均值化，防止奇异矩阵报错
    # 仅保留 Temp > 5 的点
    lap_data = lap_data[lap_data['Temp'] > 5]
    if lap_data.empty:
        continue
        
    lap_clean = lap_data.groupby(['X', 'Y']).mean(numeric_only=True).reset_index()
    
    # 观测点坐标
    xobs = lap_clean[['X', 'Y']].values
    
    # 执行各项参数插值
    field_results = {}
    try:
        for p in params:
            if p in lap_clean.columns:
                # 使用薄板样条核进行空间插值
                interp = RBFInterpolator(xobs, lap_clean[p].values, kernel='thin_plate_spline')
                yflat = interp(xflat)
                field_results[p] = yflat.reshape(x_slice, y_slice)
        
        # 保存结果，同时存入网格坐标信息
        np.savez_compressed(save_path, **field_results, grid_x=xgrid[0], grid_y=xgrid[1])
        
    except Exception as e:
        print(f"\n[错误] 处理 {file_name} 时出错: {e}")

print("\n--- 所有环境场生成完毕！ ---")
print(f"请在文件夹中查看: {SAVE_DIR}")