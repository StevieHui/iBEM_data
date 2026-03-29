import argparse
import re
import shutil
from collections import defaultdict
from pathlib import Path

import numpy as np
from shapely.geometry import Polygon, Point

# 区域坐标定义，P1..P10 对应 region_1..region_10
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

PHOTO_PATTERN = re.compile(
    r'^(RGB|Thermal)_pict_(P\d{1,2})_(\d{8})_(\d{6})\.(jpg|jpeg|png)$', re.IGNORECASE
)
ENV_PATTERN = re.compile(r'^(\d{4})_(\d+)\.npz$', re.IGNORECASE)

# 默认物理范围与分辨率
room_x_max, room_y_max = 80.105, 168.353
x_slice, y_slice = 400, 200
res_x = room_x_max / x_slice
res_y = room_y_max / y_slice


def parse_photo_filename(file_name: str):
    match = PHOTO_PATTERN.match(file_name)
    if not match:
        return None
    sensor, region, date, timepart, ext = match.groups()
    return {
        "sensor": sensor,
        "region": region,
        "date": date,
        "time": timepart,
        "ext": ext.lower(),
    }


def collect_photo_records(photo_root: Path, sensor_filter: str = "RGB"):
    records = []
    filter_value = sensor_filter.lower() if sensor_filter else "all"
    for file_path in photo_root.rglob("*"):
        if not file_path.is_file():
            continue
        parsed = parse_photo_filename(file_path.name)
        if not parsed:
            continue
        if filter_value not in {"all", "both"} and parsed["sensor"].lower() != filter_value:
            continue
        parsed["path"] = file_path
        records.append(parsed)
    return records


def assign_round_numbers(records):
    by_region_date = defaultdict(list)
    for rec in records:
        key = (rec["region"], rec["date"])
        by_region_date[key].append(rec)

    for rec_list in by_region_date.values():
        rec_list.sort(key=lambda x: x["time"])
        for idx, rec in enumerate(rec_list, start=1):
            rec["round"] = idx

    return records


def build_image_output_name(building: str, region: str, round_no: int, date: str, timepart: str, ext: str):
    return f"{building}_{region}_{round_no}_{date}_{timepart}.{ext}"


def assign_photo_env_laps(records, env_root: Path):
    env_map = collect_env_files(env_root)
    for rec in records:
        files = env_map.get(rec["date"])
        if not files:
            rec["env_lap"] = None
            continue
        if rec["round"] < 1 or rec["round"] > len(files):
            rec["env_lap"] = None
            continue
        rec["env_lap"] = files[rec["round"] - 1][0]
    return records


def copy_and_rename_photos(photo_root: Path, output_root: Path, building: str, sensor_filter: str = None, env_root: Path = None):
    records = collect_photo_records(photo_root, sensor_filter)
    if not records:
        print(f"没有在 {photo_root} 下找到符合命名规则的图片。")
        return []

    records = assign_round_numbers(records)
    if env_root:
        records = assign_photo_env_laps(records, env_root)

    output_root.mkdir(parents=True, exist_ok=True)

    renamed_records = []
    for rec in records:
        round_no = rec.get("env_lap") or rec["round"]
        new_name = build_image_output_name(
            building,
            rec["region"],
            round_no,
            rec["date"],
            rec["time"],
            rec["ext"],
        )
        dest_path = output_root / new_name
        if dest_path.exists():
            dest_path.unlink()
        shutil.copy2(rec["path"], dest_path)
        renamed_records.append({**rec, "new_path": dest_path})

    print(f"已将 {len(renamed_records)} 张图片复制并统一命名到: {output_root}")
    return renamed_records


def parse_env_filename(file_name: str):
    match = ENV_PATTERN.match(file_name)
    if not match:
        return None
    date, lap = match.group(1), int(match.group(2))
    if len(date) == 4:
        # 1215 -> 20241215
        date = f"2024{date}"
    return date, lap


def collect_env_files(env_root: Path):
    date_map = defaultdict(list)
    for path in env_root.glob("*.npz"):
        parsed = parse_env_filename(path.name)
        if not parsed:
            continue
        date, lap = parsed
        date_map[date].append((lap, path))

    for date, items in date_map.items():
        items.sort(key=lambda x: x[0])
        date_map[date] = items
    return date_map


def find_env_file_for(date: str, round_no: int, env_map):
    files = env_map.get(date)
    if not files:
        return None
    if round_no < 1 or round_no > len(files):
        return None
    return files[round_no - 1]


def load_npz_matrix(input_file: Path):
    if not input_file.exists():
        raise FileNotFoundError(f"输入文件不存在：{input_file}")
    data = np.load(input_file)
    key = list(data.keys())[0]
    return data[key], key


def extract_region_patch(full_matrix, coords):
    poly = Polygon(coords)
    minx, miny, maxx, maxy = poly.bounds

    if full_matrix.ndim == 3:
        channels, rows, cols = full_matrix.shape
    else:
        rows, cols = full_matrix.shape
        channels = 1

    c_start = max(0, int(minx / res_x))
    c_end = min(cols, int(maxx / res_x) + 1)
    r_start = max(0, int(miny / res_y))
    r_end = min(rows, int(maxy / res_y) + 1)

    if full_matrix.ndim == 3:
        patch = full_matrix[:, r_start:r_end, c_start:c_end].copy()
        ph, pw = patch.shape[1], patch.shape[2]
    else:
        patch = full_matrix[r_start:r_end, c_start:c_end].copy()
        ph, pw = patch.shape

    mask = np.zeros((ph, pw), dtype=bool)
    for r in range(ph):
        for c in range(pw):
            px = (c_start + c + 0.5) * res_x
            py = (r_start + r + 0.5) * res_y
            if poly.contains(Point(px, py)):
                mask[r, c] = True

    if full_matrix.ndim == 3:
        for ch in range(channels):
            patch[ch][~mask] = np.nan
    else:
        patch[~mask] = np.nan

    return patch, mask


def split_npz_into_regions(input_file: Path, output_dir: Path, building: str, round_no: int, timestamp: str):
    full_matrix, data_key = load_npz_matrix(input_file)
    output_dir.mkdir(parents=True, exist_ok=True)

    for idx in range(1, 11):
        region_label = f"P{idx}"
        region_key = f"region_{idx}"
        coords = regions_coords.get(region_key)
        if coords is None:
            print(f"跳过未知区域：{region_key}")
            continue

        patch, mask = extract_region_patch(full_matrix, coords)
        save_name = f"{building}_{region_label}_{round_no}_{timestamp}.npz"
        save_path = output_dir / save_name
        np.savez_compressed(save_path, **{data_key: patch, "mask": mask, "coords": np.array(coords)})
        print(f"已生成: {save_path.name}")

    print(f"全部分区文件已保存到: {output_dir}")


def split_matched_env_files(photo_records, env_root: Path, output_dir: Path, building: str):
    env_map = collect_env_files(env_root)
    if not env_map:
        print(f"在 {env_root} 中没有发现可用的 .npz 文件。")
        return

    records = assign_round_numbers(photo_records)
    output_dir.mkdir(parents=True, exist_ok=True)

    env_groups = defaultdict(list)
    for rec in records:
        env_info = find_env_file_for(rec["date"], rec["round"], env_map)
        if env_info is None:
            print(f"跳过：{rec['region']} {rec['date']} round {rec['round']}，没有对应环境场文件。")
            continue
        env_lap, env_path = env_info
        rec["env_path"] = env_path
        rec["env_lap"] = env_lap
        env_groups[env_path].append(rec)

    for env_path, recs in env_groups.items():
        full_matrix, data_key = load_npz_matrix(env_path)
        for rec in recs:
            region_index = int(rec["region"][1:])
            region_key = f"region_{region_index}"
            coords = regions_coords.get(region_key)
            if coords is None:
                print(f"跳过未知区域：{rec['region']}")
                continue

            patch, mask = extract_region_patch(full_matrix, coords)
            save_name = build_image_output_name(
                building,
                rec["region"],
                rec["env_lap"],
                rec["date"],
                rec["time"],
                "npz",
            )
            save_path = output_dir / save_name
            np.savez_compressed(save_path, **{data_key: patch, "mask": mask, "coords": np.array(coords)})
            print(f"已生成: {save_path.name}")

    print(f"已完成匹配照片的环境场分割，输出目录: {output_dir}")


def main():
    parser = argparse.ArgumentParser(description="按照片命名规则分割 Environmental Field，并统一重命名图片。")
    parser.add_argument("--photo_root", type=Path, help="照片根目录，例如 photos")
    parser.add_argument("--output_photo_dir", type=Path, default=Path("./renamed_photos"), help="复制后的图片输出目录")
    parser.add_argument("--building", type=str, default="daxing", help="建筑名称前缀，例如 da xing")
    parser.add_argument("--sensor", type=str, choices=["RGB", "Thermal", "both"], default="RGB", help="只处理指定传感器的图片。默认 RGB")
    parser.add_argument("--rename_photos", action="store_true", help="是否复制并按统一格式重命名图片")
    parser.add_argument("--env_root", type=Path, help="环境场 NPZ 文件根目录，例如 Environmental Field")
    parser.add_argument("--output_data_dir", type=Path, default=Path("./extracted_regions"), help="匹配照片后的分区 NPZ 输出目录")
    parser.add_argument("--input_file", type=Path, help="单个环境场 NPZ 文件，配合 --round/--timestamp 使用")
    parser.add_argument("--round", type=int, default=1, help="单个环境场分割时的圈数编号")
    parser.add_argument("--timestamp", type=str, help="单个环境场分割时的图像时间戳，例如 20241215_132948")
    args = parser.parse_args()

    if args.rename_photos:
        if not args.photo_root:
            raise ValueError("使用 --rename_photos 时必须指定 --photo_root")
        copy_and_rename_photos(args.photo_root, args.output_photo_dir, args.building, args.sensor, args.env_root)

    if args.env_root and args.photo_root:
        records = collect_photo_records(args.photo_root)
        if not records:
            print(f"没有在 {args.photo_root} 下找到符合命名规则的图片。")
        else:
            split_matched_env_files(records, args.env_root, args.output_data_dir, args.building)
    elif args.input_file:
        if not args.timestamp:
            raise ValueError("分割单个文件时必须指定 --timestamp")
        split_npz_into_regions(args.input_file, args.output_data_dir, args.building, args.round, args.timestamp)
    elif not args.rename_photos:
        parser.print_help()


if __name__ == "__main__":
    main()
