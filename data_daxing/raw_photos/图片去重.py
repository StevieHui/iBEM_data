import os
import shutil
from datetime import datetime
from collections import Counter


target_date = "20241225" 
base_path = r'D:\陈熠辉备份\大三上\寒假科研\ibem_data\data_daxing\photos'
TIME_THRESHOLD = 300  # 时间阈值


def process_single_folder():
    date_dir = os.path.join(base_path, target_date)
    src_dir = os.path.join(date_dir, 'RGB')  
    dst_dir = os.path.join(date_dir, 'RGB_t')

    if not os.path.exists(src_dir):
        print(f"❌ 错误：找不到源文件夹 {src_dir}")
        return

    if not os.path.exists(dst_dir):
        os.makedirs(dst_dir)
        print(f"📁 已创建目标文件夹: {dst_dir}")
    else:
        print(f"🔔 警告：目标文件夹已存在，新文件将存入其中。")

    # 1. 解析文件信息
    all_data = []
    files = [f for f in os.listdir(src_dir) if f.lower().endswith(('.jpg', '.png', '.jpeg'))]
    
    for filename in files:
        parts = filename.split('_')
        if len(parts) < 5: continue
        
        point = parts[2]                    # P1, P2...
        time_part = parts[4].split('.')[0]   # 131408
        
        try:
            dt = datetime.strptime(time_part, '%H%M%S')
            all_data.append({'filename': filename, 'point': point, 'datetime': dt})
        except ValueError:
            continue

    # 2. 排序
    all_data.sort(key=lambda x: (x['point'], x['datetime']))

    # 3. 筛选并拷贝
    last_saved = {} 
    saved_points = [] # 用于最后统计每个点位存了几张
    count = 0

    for item in all_data:
        pt = item['point']
        curr_dt = item['datetime']
        fname = item['filename']

        if pt not in last_saved:
            should_copy = True
        else:
            diff = (curr_dt - last_saved[pt]['datetime']).total_seconds()
            should_copy = diff > TIME_THRESHOLD

        if should_copy:
            shutil.copy2(os.path.join(src_dir, fname), os.path.join(dst_dir, fname))
            last_saved[pt] = item
            saved_points.append(pt)
            count += 1

    # 4. 严格的倍数校验与点位分布报告
    print("\n" + "="*40)
    print(f"📊 处理报告 - 日期: {target_date}")
    print(f"总计保留照片: {count} 张")
    
    # 统计每个点位的数量
    stats = Counter(saved_points)
    
    # 打印每个点位的分布情况，方便一眼看出哪里少了
    print("-" * 20)
    print("点位分布明细:")
    for i in range(1, 11):
        p_name = f"P{i}"
        num = stats.get(p_name, 0)
        status = "OK" if num > 0 else "MISSING ❌"
        print(f"  {p_name}: {num} 张  [{status}]")
    print("-" * 20)

    if count % 10 == 0:
        print(f"✅ 结果完美：是 10 的倍数，共 {count // 10} 圈数据。")
    else:
        remainder = count % 10
        print(f"⚠️ 校验失败：不是 10 的倍数！")
        print(f"   当前多出/缺少了 {remainder} 张照片（相对于 10 的整倍数）。")
        print(f"   请根据上方明细核对哪个点位的数据有误。")
    print("="*40)

if __name__ == "__main__":
    process_single_folder()
