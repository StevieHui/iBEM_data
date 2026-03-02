import pandas as pd
import os

# 获取当前脚本所在的文件夹路径
current_dir = os.path.dirname(os.path.abspath(__file__))

# 确保文件名和你文件夹里看到的一模一样（注意大小写和后缀）
input_file = os.path.join(current_dir, 'test_dahe_formal.csv') 
output_file = os.path.join(current_dir, 'test_dahe_formal.csv')

df = pd.read_csv(input_file)


df_cleaned = df.dropna(how='all')

    # 如果你想删除那些即使有数据但在关键列（如 Temp）缺失的行，可以使用：
    # df_cleaned = df.dropna(subset=['Temp', 'Humi'], how='any')

    # 查看处理后的行数
final_count = len(df_cleaned)

    # 保存最终结果
df_cleaned.to_csv(output_file, index=False, encoding='utf-8-sig')

print(f"✨ 清洗完成！")