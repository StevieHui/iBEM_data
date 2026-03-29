import numpy as np
import os
from shapely.geometry import Polygon, Point
from pathlib import Path

# ==========================================
# 1. 配置参数
# ==========================================
# 输入路径
input_file = r"D:\陈熠辉备份\大三上\寒假科研\ibem_data\data_daxing\Environmental Field\1212_1.npz"
output_dir = Path(r"D:\陈熠辉备份\大三上\寒假科研\ibem_data\data_daxing\Environmental Field_REGIONS\extracted_regions")

# 物理空间与分辨率
room_x_max, room_y_max = 80.105, 168.353
x_slice, y_slice = 400, 200 # 注意：矩阵形状通常是 (200, 400) -> (rows, cols)

res_x = room_x_max / x_slice
res_y = room_y_max / y_slice

regions_coords = {
    "region_1": [(37, 109), (32, 93), (23, 97), (27, 111)],
    "region_2": [(32, 93), (29, 76), (18, 78), (22, 96)],
    "region_3": [(28, 76), (26, 62), (15, 62), (17, 77)],
    "region_4": [(26, 58), (25, 45), (15, 46), (16, 60)],
    "region_5": [(40, 60), (40, 46), (27, 47), (27, 61)],
    "region_6": [(43, 73), (41, 61), (29, 61), (30, 76)],
    "region_7": [(45, 91), (43, 76), (31, 77), (34, 91)],
    "region_8": [(49, 106), (46, 92), (34, 93), (37, 106)],
    "region_9": [(53, 121), (49, 107), (38, 110), (42, 123)],
    "region_10": [(41, 125), (37, 109), (26, 111), (33, 128)],
 }
# ==========================================
# 2. 执行提取
# ==========================================

def run_extraction():
    if not os.path.exists(input_file):
        print(f"错误：未找到文件 {input_file}")
        return

    # 创建输出文件夹
    output_dir.mkdir(parents=True, exist_ok=True)

    # 加载大矩阵
    data_load = np.load(input_file)
    # 尝试自动获取 key，通常是 'data' 或 'grid'
    key = list(data_load.keys())[0]
    full_matrix = data_load[key]
    
    # 如果是多通道 [C, H, W]，此处可根据需要调整。默认取全部或指定通道。
    print(f"[*] 成功加载矩阵，Key: '{key}', 形状: {full_matrix.shape}")

    # 获取矩阵的 H, W (200, 400)
    if full_matrix.ndim == 3:
        # 假设是 (Channels, Y, X)
        channels, rows, cols = full_matrix.shape
    else:
        # 假设是 (Y, X)
        rows, cols = full_matrix.shape
        channels = 1

    for name, coords in regions_coords.items():
        poly = Polygon(coords)
        minx, miny, maxx, maxy = poly.bounds
        
        # 转换物理坐标到矩阵索引
        c_start = max(0, int(minx / res_x))
        c_end = min(cols, int(maxx / res_x) + 1)
        r_start = max(0, int(miny / res_y))
        r_end = min(rows, int(maxy / res_y) + 1)
        
        # 切取外接矩形块
        if full_matrix.ndim == 3:
            patch = full_matrix[:, r_start:r_end, c_start:c_end].copy()
            ph, pw = patch.shape[1], patch.shape[2]
        else:
            patch = full_matrix[r_start:r_end, c_start:c_end].copy()
            ph, pw = patch.shape
            
        # 生成精确的多边形掩码
        mask = np.zeros((ph, pw), dtype=bool)
        for r in range(ph):
            for c in range(pw):
                # 计算像素中心点的物理坐标
                px = (c_start + c + 0.5) * res_x
                py = (r_start + r + 0.5) * res_y
                if poly.contains(Point(px, py)):
                    mask[r, c] = True
        
        # 将多边形外的区域置为 NaN (用于保持数据纯净)
        if full_matrix.ndim == 3:
            for ch in range(channels):
                patch[ch][~mask] = np.nan
        else:
            patch[~mask] = np.nan

        # 保存为新的 .npz
        save_path = output_dir / f"{name}.npz"
        # 保持与原文件类似的存储结构
        np.savez_compressed(save_path, **{key: patch, "mask": mask, "coords": coords})
        print(f"  [-] 已生成 {name}.npz | 尺寸: {patch.shape[-2:]} | 有效像素: {np.sum(mask)}")

    print(f"\n[*] 全部处理完成！文件保存在: {output_dir}")

if __name__ == "__main__":
    run_extraction()