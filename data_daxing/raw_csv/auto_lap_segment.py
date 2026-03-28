import pandas as pd
import os

# 配置：输入/输出路径与起始标签
INPUT_PATH = r"D:\陈熠辉备份\大三上\寒假科研\ibem_data\data_daxing\raw_csv\test_daxing.csv"
OUTPUT_PATH = r"D:\陈熠辉备份\大三上\寒假科研\ibem_data\data_daxing\raw_csv\test_daxing.csv"
START_LABEL = 1 

def lap_by_start_label(df, label_col='label', start_label=START_LABEL):
    # 1. 预处理：确保 label 是整数且处理空值
    # 如果 label 是 NaN，填一个永远不会是 start_label 的值（比如 -999）
    labels = df[label_col].fillna(-999).astype(int).values
    
    laps = []
    lap_id = 1
    
    if len(labels) == 0:
        return df

    laps.append(lap_id) # 第一行
    
    # 2. 遍历判断
    for i in range(1, len(labels)):
        prev_label = labels[i-1]
        cur_label = labels[i]

        # 核心逻辑：只有当当前是起点，且上一个点不是起点时，才算新一圈
        if cur_label == start_label and prev_label != start_label:
            lap_id += 1
        
        laps.append(lap_id)

    df = df.copy()
    df['lap'] = laps
    return df

if __name__ == "__main__":
    if not os.path.exists(INPUT_PATH):
        print(f"错误：找不到输入文件 {INPUT_PATH}")
    else:
        df = pd.read_csv(INPUT_PATH)

        if 'label' not in df.columns:
            print("错误：输入文件缺少 'label' 列")
        else:
            df_with_laps = lap_by_start_label(df)
            df_with_laps.to_csv(OUTPUT_PATH, index=False)
            print(f"分圈完成！共识别出 {df_with_laps['lap'].max()} 圈")
            print(f"结果保存为：{OUTPUT_PATH}")