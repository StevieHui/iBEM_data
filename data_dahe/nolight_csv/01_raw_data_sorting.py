import pandas as pd
import numpy as np
import os

# ==== 1. 读取数据（使用了 r"" 解决路径无效字符问题） ====
# 修改第 10 行左右的路径，补上 data_dahe 这一层
df_path = r"D:\陈熠辉备份\大三上\寒假科研\ibem_data\data_dahe\raw_csv\test_dahe_light_calibrated.csv"
points_path = r"D:\陈熠辉备份\大三上\寒假科研\ibem_data\data_dahe\raw_csv\point_label.csv"

# 读取原始数据
df = pd.read_csv(df_path)
# 读取测点坐标表
points = pd.read_csv(points_path)

# 转成 numpy array 方便计算
point_coords = points[['x', 'y']].values

# ==== 2. 定义函数：找到最近的测点 ====
def find_nearest_label(x, y):
    # 如果 x 或 y 本身是 NaN，直接返回一个默认值或原样返回
    if pd.isna(x) or pd.isna(y):
        return -1 
    p = np.array([x, y])
    # 计算欧式距离：sqrt((x1-x2)^2 + (y1-y2)^2)
    dists = np.linalg.norm(point_coords - p, axis=1)
    idx = np.argmin(dists)
    return int(points.iloc[idx]['label'])

# ==== 3. 增加 label 列（核心步骤：坐标匹配） ====
print("正在匹配最近测点 label...")
df['label'] = df.apply(lambda row: find_nearest_label(row['x'], row['y']), axis=1)

# ==== 4. 删除 Temp = 0 的行 ====
df = df.loc[(df['Temp'] != 0)]
df = df.reset_index(drop=True)

# ------------------------------------------------------------
# 🔥 6. 数值保留位数（修复 IntCastingNaNError）
# ------------------------------------------------------------

# Temp 保留 1 位小数
df['Temp'] = df['Temp'].round(1)

# 其他参数全部取整
int_cols = ['Humi', 'Light', 'CO2', 'PM10', 'PM2.5', 'PM1', 'noise']
for col in int_cols:
    if col in df.columns:
        # 1. 强制转为数值，无法转换的变 NaN
        df[col] = pd.to_numeric(df[col], errors='coerce')
        # 2. 填充空值（比如填 0），防止转 int 时报错
        df[col] = df[col].fillna(0).round().astype(int)

# ------------------------------------------------------------

# ==== 7. 保存结果 ====
output_path = r"D:\陈熠辉备份\大三上\寒假科研\ibem_data\data_dahe\raw_csv\test_dahe_light_calibrated_label.csv"
df.to_csv(output_path, index=False)

print(f"处理完成！匹配了 {len(df)} 行数据，已保存到：{output_path}")