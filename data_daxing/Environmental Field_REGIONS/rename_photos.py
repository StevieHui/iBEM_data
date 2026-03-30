import argparse
import re
import shutil
import sys
from collections import defaultdict
from pathlib import Path

PHOTO_PATTERN = re.compile(
    r'^(RGB|Thermal)_pict_(P\d{1,2})_(\d{8})_(\d{6})\.(jpg|jpeg|png)$', re.IGNORECASE
)
ENV_PATTERN = re.compile(r'^(\d{4}|\d{8})_(\d+)\.npz$', re.IGNORECASE)


def parse_photo_filename(file_name: str):
    match = PHOTO_PATTERN.match(file_name)
    if not match:
        return None
    sensor, region, date, timepart, ext = match.groups()
    return {
        'sensor': sensor,
        'region': region,
        'date': date,
        'time': timepart,
        'ext': ext.lower(),
    }


def parse_env_filename(file_name: str):
    match = ENV_PATTERN.match(file_name)
    if not match:
        return None
    date, lap = match.group(1), int(match.group(2))
    if len(date) == 4:
        date = f'2024{date}'
    return date, lap


def collect_photo_records(photo_root: Path, sensor_filter: str = 'RGB'):
    records = []
    filter_value = sensor_filter.lower() if sensor_filter else 'all'
    for file_path in photo_root.rglob('*'):
        if not file_path.is_file():
            continue
        parsed = parse_photo_filename(file_path.name)
        if not parsed:
            continue
        if filter_value not in {'all', 'both'} and parsed['sensor'].lower() != filter_value:
            continue
        parsed['path'] = file_path
        records.append(parsed)
    return records


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


def assign_round_numbers(records):
    by_region_date = defaultdict(list)
    for rec in records:
        key = (rec['region'], rec['date'])
        by_region_date[key].append(rec)

    for rec_list in by_region_date.values():
        rec_list.sort(key=lambda x: x['time'])
        for idx, rec in enumerate(rec_list, start=1):
            rec['round'] = idx

    return records


def validate_photo_counts(records):
    by_date = defaultdict(list)
    for rec in records:
        by_date[rec['date']].append(rec)

    for date, date_records in by_date.items():
        region_rounds = defaultdict(set)
        for rec in date_records:
            region_rounds[rec['region']].add(rec['round'])

        rounds_per_region = []
        for region, rounds in region_rounds.items():
            if not rounds:
                continue
            max_round = max(rounds)
            if rounds != set(range(1, max_round + 1)):
                print(
                    f'警告：{date} 日区域 {region} 的圈数不连续，检测到 {len(rounds)} 个圈数，实际值为 {sorted(rounds)}。'
                )
                print('已停止重命名，请检查图片是否缺失或多余。')
                return False
            rounds_per_region.append(max_round)

        if not rounds_per_region:
            continue

        if len(set(rounds_per_region)) != 1:
            print(
                f'警告：{date} 日各点位圈数不一致，检测到每个点位圈数 {rounds_per_region}。'
            )
            print('已停止重命名，请检查图片是否缺失或多余。')
            return False

        point_count = len(region_rounds)
        daily_rounds = rounds_per_region[0]
        expected = point_count * daily_rounds
        actual = len(date_records)
        if actual != expected:
            print(
                f'警告：{date} 日照片数量不符合预期。检测到 {actual} 张，点位数 {point_count}，当天圈数 {daily_rounds}，预期 {expected}。'
            )
            print('已停止重命名，请检查图片是否缺失或多余。')
            return False

    return True


def assign_photo_env_laps(records, env_root: Path):
    env_map = collect_env_files(env_root)
    for rec in records:
        files = env_map.get(rec['date'])
        if not files:
            rec['env_lap'] = None
            continue
        if rec['round'] < 1 or rec['round'] > len(files):
            rec['env_lap'] = None
            continue
        rec['env_lap'] = files[rec['round'] - 1][0]
    return records


def build_output_name(building: str, region: str, round_no: int, date: str, timepart: str, ext: str):
    return f'{building}_{region}_{round_no}_{date}_{timepart}.{ext}'


def rename_photos(photo_root: Path, output_root: Path, building: str, sensor_filter: str, env_root: Path = None):
    records = collect_photo_records(photo_root, sensor_filter)
    if not records:
        print(f'没有在 {photo_root} 下找到符合命名规则的图片。')
        return []

    records = assign_round_numbers(records)
    if not validate_photo_counts(records):
        return []

    if env_root:
        records = assign_photo_env_laps(records, env_root)

    output_root.mkdir(parents=True, exist_ok=True)
    renamed = []
    for rec in records:
        round_no = rec.get('env_lap') or rec['round']
        new_name = build_output_name(
            building,
            rec['region'],
            round_no,
            rec['date'],
            rec['time'],
            rec['ext'],
        )
        dest_path = output_root / new_name
        if dest_path.exists():
            dest_path.unlink()
        shutil.copy2(rec['path'], dest_path)
        renamed.append({**rec, 'new_path': dest_path})

    print(f'已将 {len(renamed)} 张图片复制并统一命名到: {output_root}')
    return renamed


def main():
    parser = argparse.ArgumentParser(description='仅重命名并复制照片，支持按环境场文件圈数映射命名。')
    parser.add_argument('--photo_root', type=Path, required=True, help='照片根目录，例如 photos')
    parser.add_argument('--output_photo_dir', type=Path, required=True, help='输出目录，例如 Environmental Field_REGIONS/photos')
    parser.add_argument('--building', type=str, default='daxing', help='建筑名称前缀，例如 da xing')
    parser.add_argument('--sensor', type=str, choices=['RGB', 'Thermal', 'both'], default='RGB', help='选择处理的传感器')
    parser.add_argument('--env_root', type=Path, help='可选：环境场 NPZ 根目录，用于按圈数映射命名')
    args = parser.parse_args()

    rename_photos(args.photo_root, args.output_photo_dir, args.building, args.sensor, args.env_root)


if __name__ == '__main__':
    main()
