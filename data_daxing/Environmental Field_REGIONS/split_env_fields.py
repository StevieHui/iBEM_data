import argparse
import re
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np

# 避免当前目录下的 Shapely.py shadow 已安装的 shapely 包
if sys.path:
    cwd_path = Path(__file__).resolve().parent
    if Path(sys.path[0]).resolve() == cwd_path:
        _saved_sys_path0 = sys.path.pop(0)
    else:
        _saved_sys_path0 = None
try:
    from shapely.geometry import Polygon, Point
except ImportError:
    raise ImportError('请先安装 shapely，或者不要让本目录下的 Shapely.py 与 shapely 包冲突。')
finally:
    if _saved_sys_path0 is not None:
        sys.path.insert(0, _saved_sys_path0)

regions_coords = {
    'region_1': [(37, 109), (32, 93), (23, 97), (27, 111)],
    'region_2': [(32, 93), (29, 76), (18, 78), (22, 96)],
    'region_3': [(28, 76), (26, 62), (15, 62), (17, 77)],
    'region_4': [(26, 58), (25, 45), (15, 46), (16, 60)],
    'region_5': [(40, 60), (40, 46), (27, 47), (27, 61)],
    'region_6': [(43, 73), (41, 61), (29, 61), (30, 76)],
    'region_7': [(45, 91), (43, 76), (31, 77), (34, 91)],
    'region_8': [(49, 106), (46, 92), (34, 93), (37, 106)],
    'region_9': [(53, 121), (49, 107), (38, 110), (42, 123)],
    'region_10': [(41, 125), (37, 109), (26, 111), (33, 128)],
}

PHOTO_PATTERN = re.compile(
    r'^(RGB|Thermal)_pict_(P\d{1,2})_(\d{8})_(\d{6})\.(jpg|jpeg|png)$', re.IGNORECASE
)
RENAMED_PHOTO_PATTERN = re.compile(
    r'^(.+?)_(P\d{1,2})_(\d+)_(\d{8})_(\d{6})\.(jpg|jpeg|png)$', re.IGNORECASE
)
ENV_PATTERN = re.compile(r'^(\d{4}|\d{8})_(\d+)\.npz$', re.IGNORECASE)

room_x_max, room_y_max = 80.105, 168.353
x_slice, y_slice = 400, 200
res_x = room_x_max / x_slice
res_y = room_y_max / y_slice


def parse_photo_filename(file_name: str):
    match = PHOTO_PATTERN.match(file_name)
    if match:
        sensor, region, date, timepart, ext = match.groups()
        return {
            'sensor': sensor,
            'region': region,
            'date': date,
            'time': timepart,
            'round': None,
            'ext': ext.lower(),
        }

    match = RENAMED_PHOTO_PATTERN.match(file_name)
    if match:
        _, region, round_no, date, timepart, ext = match.groups()
        return {
            'sensor': None,
            'region': region,
            'date': date,
            'time': timepart,
            'round': int(round_no),
            'ext': ext.lower(),
        }

    return None


def collect_photo_records(photo_root: Path, sensor_filter: str = 'RGB'):
    records = []
    filter_value = sensor_filter.lower() if sensor_filter else 'all'
    for path in photo_root.rglob('*'):
        if not path.is_file():
            continue
        parsed = parse_photo_filename(path.name)
        if not parsed:
            continue
        if parsed['sensor'] is None:
            parent = path.parent.name
            if parent.lower() in {'rgb', 'thermal'}:
                parsed['sensor'] = parent.upper()
        if filter_value not in {'all', 'both'}:
            if parsed['sensor'] is None or parsed['sensor'].lower() != filter_value:
                continue
        parsed['path'] = path
        records.append(parsed)
    return records


def assign_round_numbers(records):
    by_region_date = defaultdict(list)
    for rec in records:
        key = (rec['region'], rec['date'])
        by_region_date[key].append(rec)

    for rec_list in by_region_date.values():
        if all(rec.get('round') for rec in rec_list):
            continue
        rec_list.sort(key=lambda x: x['time'])
        for idx, rec in enumerate(rec_list, start=1):
            rec['round'] = idx

    return records


def find_env_file_for(date: str, round_no: int, env_map):
    files = env_map.get(date)
    if not files:
        return None
    # 先尝试按真实环境场圈数匹配（例如 1215_5 -> lap 5）
    for lap, path in files:
        if lap == round_no:
            return lap, path
    # 再尝试按照片顺序的 round 号匹配
    if 1 <= round_no <= len(files):
        return files[round_no - 1]
    return None


def split_matched_env_files(photo_records, env_root: Path, output_dir: Path, building: str):
    env_map = collect_env_files(env_root)
    if not env_map:
        print(f'在 {env_root} 中没有发现符合格式的 .npz 文件。')
        return

    photo_records = assign_round_numbers(photo_records)
    output_dir.mkdir(parents=True, exist_ok=True)

    env_groups = defaultdict(list)
    for rec in photo_records:
        env_info = find_env_file_for(rec['date'], rec['round'], env_map)
        if env_info is None:
            print(f"跳过：{rec['region']} {rec['date']} round {rec['round']}，没有对应环境场文件。")
            continue
        env_lap, env_path = env_info
        rec['env_path'] = env_path
        rec['env_lap'] = env_lap
        env_groups[env_path].append(rec)

    for env_path, recs in env_groups.items():
        full_matrix, data_key = load_npz_matrix(env_path)
        for rec in recs:
            region_index = int(rec['region'][1:])
            region_key = f'region_{region_index}'
            coords = regions_coords.get(region_key)
            if coords is None:
                print(f"跳过未知区域：{rec['region']}")
                continue

            patch, mask = extract_region_patch(full_matrix, coords)
            save_name = f"{building}_{rec['region']}_{rec['env_lap']}_{rec['date']}_{rec['time']}.npz"
            save_path = output_dir / save_name
            np.savez_compressed(save_path, **{data_key: patch, 'mask': mask, 'coords': np.array(coords)})
            print(f'已生成: {save_path.name}')

    print(f'已完成匹配照片的环境场分割，输出目录: {output_dir}')


def split_matched_single_env_file(photo_records, input_file: Path, output_dir: Path, building: str):
    parsed = parse_env_filename(input_file.name)
    if not parsed:
        raise ValueError(f'输入文件名不符合格式: {input_file.name}')

    date, lap = parsed
    photo_records = [rec for rec in photo_records if rec['date'] == date]
    if not photo_records:
        print(f'在 {input_file} 对应的日期 {date} 没有找到符合命名规则的照片。')
        return

    photo_records = assign_round_numbers(photo_records)
    matched = [rec for rec in photo_records if rec['round'] == lap]
    if not matched:
        print(f'在 {date} 没有找到对应圈数 {lap} 的照片。')
        return

    full_matrix, data_key = load_npz_matrix(input_file)
    output_dir.mkdir(parents=True, exist_ok=True)

    for rec in matched:
        region_index = int(rec['region'][1:])
        region_key = f'region_{region_index}'
        coords = regions_coords.get(region_key)
        if coords is None:
            print(f"跳过未知区域：{rec['region']}")
            continue

        patch, mask = extract_region_patch(full_matrix, coords)
        save_name = f"{building}_{rec['region']}_{lap}_{date}_{rec['time']}.npz"
        save_path = output_dir / save_name
        np.savez_compressed(save_path, **{data_key: patch, 'mask': mask, 'coords': np.array(coords)})
        print(f'已生成: {save_path.name}')

    print(f'已完成匹配单个环境场文件 {input_file.name} 的输出，保存到: {output_dir}')


def parse_env_filename(file_name: str):
    match = ENV_PATTERN.match(file_name)
    if not match:
        return None
    date, lap = match.group(1), int(match.group(2))
    if len(date) == 4:
        date = f'2024{date}'
    return date, lap


def collect_env_files(env_root: Path):
    date_map = defaultdict(list)
    for path in env_root.glob('*.npz'):
        parsed = parse_env_filename(path.name)
        if not parsed:
            continue
        date, lap = parsed
        date_map[date].append((lap, path))

    for date, items in date_map.items():
        items.sort(key=lambda x: x[0])
        date_map[date] = items
    return date_map


def load_npz_matrix(input_file: Path):
    if not input_file.exists():
        raise FileNotFoundError(f'输入文件不存在：{input_file}')
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


def split_single_env_file(input_file: Path, output_dir: Path, building: str):
    parsed = parse_env_filename(input_file.name)
    if not parsed:
        raise ValueError(f'输入文件名不符合格式: {input_file.name}')
    date, lap = parsed
    full_matrix, data_key = load_npz_matrix(input_file)
    output_dir.mkdir(parents=True, exist_ok=True)

    for idx in range(1, 11):
        region_label = f'P{idx}'
        region_key = f'region_{idx}'
        coords = regions_coords[region_key]
        patch, mask = extract_region_patch(full_matrix, coords)
        save_name = f'{building}_{region_label}_{lap}_{date}.npz'
        save_path = output_dir / save_name
        np.savez_compressed(save_path, **{data_key: patch, 'mask': mask, 'coords': np.array(coords)})
        print(f'已生成: {save_path.name}')

    print(f'已将 {input_file.name} 拆分为 10 个区域文件，保存到: {output_dir}')


def split_env_directory(env_root: Path, output_dir: Path, building: str):
    env_map = collect_env_files(env_root)
    if not env_map:
        print(f'在 {env_root} 中没有发现符合格式的 .npz 文件。')
        return

    output_dir.mkdir(parents=True, exist_ok=True)
    for date, files in env_map.items():
        for lap, env_path in files:
            full_matrix, data_key = load_npz_matrix(env_path)
            for idx in range(1, 11):
                region_label = f'P{idx}'
                region_key = f'region_{idx}'
                coords = regions_coords[region_key]
                patch, mask = extract_region_patch(full_matrix, coords)
                save_name = f'{building}_{region_label}_{lap}_{date}.npz'
                save_path = output_dir / save_name
                np.savez_compressed(save_path, **{data_key: patch, 'mask': mask, 'coords': np.array(coords)})
            print(f'已拆分: {env_path.name} -> {output_dir}')

    print(f'全部环境场文件已拆分并保存到: {output_dir}')


def main():
    parser = argparse.ArgumentParser(description='拆分环境场 NPZ 为 10 个区域文件。')
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--env_root', type=Path, help='环境场 NPZ 目录，例如 Environmental Field')
    group.add_argument('--input_file', type=Path, help='单个环境场 NPZ 文件')
    parser.add_argument('--photo_root', type=Path, help='可选：照片根目录，用于按照片时间戳映射环境场输出文件名')
    parser.add_argument('--sensor', type=str, choices=['RGB', 'Thermal', 'both'], default='RGB', help='选择处理的传感器')
    parser.add_argument('--output_dir', type=Path, default=Path('./extracted_regions'), help='输出目录')
    parser.add_argument('--building', type=str, default='daxing', help='输出文件前缀名称')
    args = parser.parse_args()

    if args.photo_root and not args.env_root and not args.input_file:
        parser.error('--photo_root 需要配合 --env_root 或 --input_file 使用。')

    if args.input_file:
        if args.photo_root:
            photo_records = collect_photo_records(args.photo_root, args.sensor)
            if photo_records:
                split_matched_single_env_file(photo_records, args.input_file, args.output_dir, args.building)
            else:
                print(f'在 {args.photo_root} 中未找到符合命名规则的照片。')
        else:
            split_single_env_file(args.input_file, args.output_dir, args.building)
    else:
        if args.photo_root:
            photo_records = collect_photo_records(args.photo_root, args.sensor)
            if photo_records:
                split_matched_env_files(photo_records, args.env_root, args.output_dir, args.building)
            else:
                print(f'在 {args.photo_root} 中未找到符合命名规则的照片。')
        else:
            split_env_directory(args.env_root, args.output_dir, args.building)


if __name__ == '__main__':
    main()
