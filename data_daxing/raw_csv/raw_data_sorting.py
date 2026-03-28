import pandas as pd
import numpy as np

# ==== 1. 配置路径 ====
df_path = r"D:\陈熠辉备份\大三上\寒假科研\ibem_data\data_daxing\raw_csv\test_daxing.csv"
points_path = r"D:\陈熠辉备份\大三上\寒假科研\ibem_data\data_daxing\raw_csv\point_label.csv"
output_path = r"D:\陈熠辉备份\大三上\寒假科研\ibem_data\data_daxing\raw_csv\test_daxing.csv"

# 读取数据
df = pd.read_csv(df_path)
points = pd.read_csv(points_path)

# 获取测点参考坐标
point_coords = points[['X2', 'Y2']].values

# ==== 2. 坐标匹配函数 ====
def find_nearest_label(x, y):
    if pd.isna(x) or pd.isna(y):
        return -1 
    p = np.array([x, y])
    dists = np.linalg.norm(point_coords - p, axis=1)
    idx = np.argmin(dists)
    return int(points.iloc[idx]['label'])

# ==== 3. 执行核心逻辑 ====

# A. 坐标匹配产生新的 label
print("正在匹配最近测点 label...")
df['label'] = df.apply(lambda row: find_nearest_label(row['X2'], row['Y2']), axis=1)

# B. 删除温度为 0 的无效行
df = df.loc[df['Temp'] != 0].copy()

# C. 温度保留一位小数
df['Temp'] = df['Temp'].round(1)

# D. 其他环境参数全部取整 (你要求的逻辑)
int_cols = ['Humi', 'Light', 'CO2', 'PM10', 'PM2.5', 'PM1', 'noise']
for col in int_cols:
    if col in df.columns:
        # 强制转为数值，无法转换的变为 NaN
        df[col] = pd.to_numeric(df[col], errors='coerce')
        # 填充空值为 0，四舍五入后转为整数
        df[col] = df[col].fillna(0).round().astype(int)

# ==== 4. 保存结果 ====
df.to_csv(output_path, index=False)
print(f"处理完成！daxing 数据已保存至: {output_path}")