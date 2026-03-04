import pandas as pd
import os

# ==========================================
# 1. 真实修正系数 (基于你的回归结果)
# ==========================================
CALIBRATION_PARAMS = {
    # 格式: '列名': (斜率a, 截距b)
    'Temp':  (0.835, 4.2014),
    'Humi':  (0.9242, 3.8854),
    'Light': (1.0533, -0.0354),
    # 以下为占位符，若无系数可保持 (1.0, 0.0)
    'CO2':   (1.0, 0.0),
    'PM10':  (1.0, 0.0),
    'PM2.5': (1.0, 0.0),
    'PM1':   (1.0, 0.0),
    'noise': (1.0, 0.0)
}

# 故障检测列：若这些列读数为 0，则整行剔除
SENSOR_COLUMNS = ['Temp', 'Humi', 'PM2.5', 'PM10', 'PM1', 'CO2']

def clean_and_calibrate(df):
    # 线性校准 ---
    for col, (a, b) in CALIBRATION_PARAMS.items():
        if col in df.columns:
            # 核心计算：y = ax + b
            df[col] = a * df[col] + b
            
            # 物理边界：Light/PM/CO2 不能为负
            if col in ['Light', 'CO2', 'PM2.5', 'PM10', 'PM1']:
                df[col] = df[col].clip(lower=0)
                
    return df

def main():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    # 请确保文件名与你本地一致
    input_file = os.path.join(current_dir, 'test_dahe_formal.csv')
    output_file = os.path.join(current_dir, 'test_dahe_light_calibrated.csv')

    if not os.path.exists(input_file):
        print(f"❌ 找不到文件: {input_file}")
        return

    df = pd.read_csv(input_file, encoding='utf-8-sig')
    df.columns = df.columns.str.strip()

    df_final = clean_and_calibrate(df)

    df_final.to_csv(output_file, index=False, encoding='utf-8-sig')
    print(f"✅ 校准成功！")
    print(f"📊 最终有效样本数: {len(df_final)}")
    print(f"💾 文件保存在: {output_file}")

if __name__ == "__main__":
    main()