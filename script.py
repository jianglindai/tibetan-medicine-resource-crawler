#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
功能：为中药数据添加唯一 ID 和顺序 ID，并生成 JSONL 和关键词文件
输入：results/nwipb_20260904_052246.json
输出：results/nwipb_20260904_052246.jsonl 和 results/keyword.txt
run: python script.py
"""


import json
import hashlib
import sys
import os
from collections import OrderedDict

def generate_hash_id(scientific_name: str) -> str:
    """根据 scientific_name 生成 MD5 哈希 ID（十六进制）"""
    return hashlib.md5(scientific_name.encode('utf-8')).hexdigest()

def reorder_dict(obj, id_key='id', seq_key='seq_id'):
    """
    重新排序字典，将 id 和 seq_id 放在最前面。
    返回一个新的 OrderedDict，保证字段顺序。
    """
    new_obj = OrderedDict()
    if id_key in obj:
        new_obj[id_key] = obj[id_key]
    if seq_key in obj:
        new_obj[seq_key] = obj[seq_key]
    for key, value in obj.items():
        if key not in (id_key, seq_key):
            new_obj[key] = value
    return new_obj

def process_data(data, id_func):
    """
    处理数据：
    - 为每个包含 scientific_name 的字典添加 'id'（哈希）
    - 为每个对象添加 'seq_id'（从1开始递增）
    支持根为列表或单个字典。
    返回处理后的数据（结构不变，但每个对象内部顺序随后调整）。
    """
    if isinstance(data, list):
        for idx, item in enumerate(data, start=1):
            if isinstance(item, dict) and 'scientific_name' in item:
                item['id'] = id_func(item['scientific_name'])
                item['seq_id'] = idx
    elif isinstance(data, dict):
        if 'scientific_name' in data:
            data['id'] = id_func(data['scientific_name'])
            data['seq_id'] = 1
    else:
        raise TypeError("JSON 根必须为列表或字典对象")
    return data

def extract_scientific_names(data):
    """
    从数据中提取所有 scientific_name，按原顺序返回列表。
    如果根是列表，逐个提取；如果是单个对象，直接提取。
    """
    names = []
    if isinstance(data, list):
        for item in data:
            if isinstance(item, dict) and 'scientific_name' in item:
                names.append(item['scientific_name'])
    elif isinstance(data, dict):
        if 'scientific_name' in data:
            names.append(data['scientific_name'])
    return names

def write_jsonl(data, output_file):
    """将数据以 JSONL 格式写入文件，每行一个对象，字段顺序调整为 id、seq_id 优先。"""
    # 确保输出目录存在
    os.makedirs(os.path.dirname(os.path.abspath(output_file)), exist_ok=True)
    with open(output_file, 'w', encoding='utf-8') as f:
        if isinstance(data, list):
            for obj in data:
                ordered_obj = reorder_dict(obj)
                f.write(json.dumps(ordered_obj, ensure_ascii=False) + '\n')
        elif isinstance(data, dict):
            ordered_obj = reorder_dict(data)
            f.write(json.dumps(ordered_obj, ensure_ascii=False) + '\n')
        else:
            raise TypeError("数据根必须为列表或字典")

def write_keywords(names, output_file='keyword.txt'):
    """将 scientific_name 列表逐行写入文本文件。"""
    # 确保输出目录存在
    os.makedirs(os.path.dirname(os.path.abspath(output_file)), exist_ok=True)
    with open(output_file, 'w', encoding='utf-8') as f:
        for name in names:
            f.write(name + '\n')

def main(input_file: str, output_jsonl: str = None, keyword_file: str = None):
    # 自动生成输出 JSONL 文件名
    if output_jsonl is None:
        base, _ = os.path.splitext(input_file)
        output_jsonl = f"{base}.jsonl"

    # 如果未指定关键词文件，默认放在 results 目录下
    if keyword_file is None:
        # 从输入文件所在目录提取父目录，通常为 'results'
        base_dir = os.path.dirname(input_file)
        if base_dir:
            keyword_file = os.path.join(base_dir, 'keyword.txt')
        else:
            keyword_file = 'keyword.txt'  # 若输入就在当前目录，则保持当前目录

    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"错误：找不到文件 '{input_file}'", file=sys.stderr)
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"错误：JSON 解析失败 - {e}", file=sys.stderr)
        sys.exit(1)

    # 1. 添加 ID 和顺序 ID
    data = process_data(data, generate_hash_id)

    # 2. 提取 scientific_name（在添加 ID 之后，但不会影响原始字段）
    names = extract_scientific_names(data)

    # 3. 写出 JSONL
    write_jsonl(data, output_jsonl)
    print(f"JSONL 已保存：{output_jsonl}")

    # 4. 写出 keyword.txt
    write_keywords(names, keyword_file)
    print(f"关键词已提取保存：{keyword_file} (共 {len(names)} 条)")

if __name__ == '__main__':
    # 命令行参数：第一个为输入文件，第二个为输出 JSONL（可选），第三个为关键词文件（可选）
    if len(sys.argv) > 1:
        input_file = sys.argv[1]
        output_jsonl = sys.argv[2] if len(sys.argv) > 2 else None
        keyword_file = sys.argv[3] if len(sys.argv) > 3 else None
        main(input_file, output_jsonl, keyword_file)
    else:
        # 默认处理 results 目录下的文件（脚本与 results 同级）
        main('results/nwipb_20260904_052246.json')