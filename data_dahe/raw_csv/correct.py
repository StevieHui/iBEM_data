import pandas as pd
import os
from scipy import stats

# 1. 读取数据
current_dir = os.path.dirname(os.path.abspath(__file__))
file_raw = os.path.join(current_dir, 'test_dahe_konghang.csv')
file_corr = os.path.join(current_dir, '大河村数据修正采集数据（温湿度光照）0521_0524 的副本.csv')

# 统一使用 utf-8-sig 处理中文
df_raw = pd.read_csv(file_raw, encoding='utf-8-sig')
df_corr = pd.read_csv(file_corr, encoding='utf-8-sig')

# 2. 预处理：清理空格 + 转换时间对象
df_raw.columns = df_raw.columns.str.strip()
df_corr.columns = df_corr.columns.str.strip()

# 强制将时间转为标准 datetime 对象，确保对齐逻辑一致
time_col = 'Time' # 如果你的列名是大写 'Time'，请手动修改这里
df_raw[time_col] = pd.to_datetime(df_raw[time_col])
df_corr[time_col] = pd.to_datetime(df_corr[time_col])

# 3. 核心步骤：基于时间的 Inner Merge (只保留交集)
# 这能保证每一行 raw 对应的都是同一时刻的 corr
df_merged = pd.merge(df_raw, df_corr, on=time_col, suffixes=('_raw', '_corr'))

print(f"📊 原始数据: {len(df_raw)} 行 | 修正数据: {len(df_corr)} 行")
print(f"🔗 对齐成功: {len(df_merged)} 行")

# 【重要检查】看看前5行是否真的对应上了
print("\n👀 对齐核对（前5行）：")
print(df_merged[[time_col, 'Temp_raw', 'Temp_corr']].head())

# 4. 重新计算回归
cols = ['Temp', 'Humi', 'Light']
for col in cols:
    r_col, c_col = f"{col}_raw", f"{col}_corr"
    if r_col in df_merged.columns and c_col in df_merged.columns:
        # 剔除空值
        valid = df_merged[[r_col, c_col]].dropna()
        slope, intercept, r_val, p_val, std_err = stats.linregress(valid[r_col], valid[c_col])
        
        print(f"\n🔹 {col} 结果:")
        print(f"   拟合方程: y = {slope:.4f}x + ({intercept:.4f})")
        print(f"   相关系数 R²: {r_val**2:.6f}")