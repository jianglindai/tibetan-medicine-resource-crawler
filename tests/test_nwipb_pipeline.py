"""JsonWriterPipeline / CsvWriterPipeline 单元测试"""

import csv
import json
from unittest.mock import MagicMock

from tibetanMedResourceSpider.pipelines import CsvWriterPipeline, JsonWriterPipeline


# ── JsonWriterPipeline ──────────────────────────────────


def test_json_writer_writes_all_items(tmp_path):
    """多条记录 → 写入 output.json"""
    pipeline = JsonWriterPipeline(output_dir=str(tmp_path), filename="medicines.json")

    spider = MagicMock()
    pipeline.open_spider(spider)

    items = [
        {"scientific_name": "红景天", "latin_name": "Rhodiola", "images": []},
        {"scientific_name": "川贝母", "latin_name": "Fritillaria", "images": []},
    ]
    for item in items:
        pipeline.process_item(item, spider)

    pipeline.close_spider(spider)

    filepath = tmp_path / "medicines.json"
    assert filepath.exists()
    with open(filepath, encoding="utf-8") as f:
        data = json.load(f)
    assert len(data) == 2
    assert data[0]["scientific_name"] == "红景天"
    assert data[1]["latin_name"] == "Fritillaria"


def test_json_writer_flush_on_interval(tmp_path):
    """每 10 条触发一次中间写入，确保数据不丢失"""
    pipeline = JsonWriterPipeline(output_dir=str(tmp_path))

    spider = MagicMock()
    pipeline.open_spider(spider)

    for i in range(25):
        pipeline.process_item({"scientific_name": f"药材{i}"}, spider)

    filepath = tmp_path / "output.json"
    assert filepath.exists()

    pipeline.close_spider(spider)
    with open(filepath, encoding="utf-8") as f:
        data = json.load(f)
    assert len(data) == 25


def test_json_writer_empty_no_file(tmp_path):
    """无数据时不应产生文件"""
    pipeline = JsonWriterPipeline(output_dir=str(tmp_path))

    spider = MagicMock()
    pipeline.open_spider(spider)
    pipeline.close_spider(spider)

    files = list(tmp_path.iterdir())
    assert len(files) == 0


# ── CsvWriterPipeline ───────────────────────────────────


def test_csv_writer_writes_header_and_rows(tmp_path):
    """CSV 输出包含表头与数据行"""
    pipeline = CsvWriterPipeline(output_dir=str(tmp_path), filename="medicines.csv")

    spider = MagicMock()
    pipeline.open_spider(spider)

    items = [
        {"scientific_name": "红景天", "aliases": ["A", "B"], "images": [{"url": "http://x"}]},
        {"scientific_name": "川贝母", "aliases": ["C"], "images": []},
    ]
    for item in items:
        pipeline.process_item(item, spider)

    pipeline.close_spider(spider)

    filepath = tmp_path / "medicines.csv"
    assert filepath.exists()
    with open(filepath, encoding="utf-8-sig", newline="") as f:
        reader = csv.reader(f)
        rows = list(reader)

    # 表头 + 2 行数据
    assert len(rows) == 3
    assert "scientific_name" in rows[0]
    # list 字段以 "; " 连接
    aliases_col = rows[0].index("aliases")
    assert rows[1][aliases_col] == "A; B"
    # 嵌套 dict list 以 JSON 字符串保存
    images_col = rows[0].index("images")
    assert "http://x" in rows[1][images_col]


# ── MedicineRecord 数据模型 ─────────────────────────────


def test_medicine_record_to_dict_and_from_dict():
    """数据模型序列化/反序列化往返测试"""
    from tibetanMedResourceSpider.spiders.models import MedicineImage, MedicineRecord

    record = MedicineRecord(
        scientific_name="红景天",
        latin_name="Rhodiola crenulata",
        aliases=["大花红景天", "苏罗玛宝"],
        medicine_name="红景天",
        medicinal_parts=["根及根茎"],
        functions_and_indications="益气活血，通脉平喘",
        images=[MedicineImage(url="http://example.com/1.jpg", alt="红景天")],
        source_url="http://example.com/1",
        crawled_at="2026-08-19T00:00:00+00:00",
    )

    d = record.to_dict()
    assert d["scientific_name"] == "红景天"
    assert d["aliases"] == ["大花红景天", "苏罗玛宝"]
    assert d["images"][0]["url"] == "http://example.com/1.jpg"

    restored = MedicineRecord.from_dict(d)
    assert restored.scientific_name == record.scientific_name
    assert restored.aliases == record.aliases
    assert restored.images[0].url == record.images[0].url
