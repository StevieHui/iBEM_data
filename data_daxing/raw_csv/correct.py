import pandas as pd
import os

# 获取当前脚本所在的文件夹路径
current_dir = os.path.dirname(os.path.abspath(__file__))

# 确保文件名和你文件夹里看到的一模一样（注意大小写和后缀）
input_file = os.path.join(current_dir, 'test_daxing.csv') 
output_file = os.path.join(current_dir, 'test_daxing_corrected.csv')

# 检查文件是否存在
if not os.path.exists(input_file):
    print(f"❌ 找不到文件！请检查：{input_file}")
    print(f"当前文件夹下的文件有：{os.listdir(current_dir)}")
else:
    # 读取数据
    df = pd.read_csv(input_file)

    # 环境参数修正
    # 注意：请确保 CSV 里的列名确实是 'Temp', 'Humi' 等，如果不对会报错
    df['Temp'] = df['Temp'] + 0.49
    df['Humi'] = df['Humi'] - 1.15
    df['Light'] = df['Light'] - 80
    df['CO2'] = df['CO2'] - 369.34
    df['PM2.5'] = df['PM2.5'] - 0.69

    # 【关键操作】删除空行
    # how='all' 表示只有整行全为空时才删除
    # how='any' 表示只要该行有一个空格就删除（根据科研需求通常选 all 或指定关键列）
    df_cleaned = df.dropna(how='all')

    # 如果你想删除那些即使有数据但在关键列（如 Temp）缺失的行，可以使用：
    # df_cleaned = df.dropna(subset=['Temp', 'Humi'], how='any')

    # 查看处理后的行数
    final_count = len(df_cleaned)

    # 保存最终结果
    df_cleaned.to_csv(output_file, index=False, encoding='utf-8-sig')

    print(f"✨ 清洗完成！")

