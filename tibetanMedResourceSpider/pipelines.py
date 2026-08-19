"""藏药材数据管道

提供 JSON / CSV 两种输出管道。默认未启用（settings.py 中 ITEM_PIPELINES 为空），
由 Scrapy 内置 FEEDS 处理输出。如需自定义管道，可在 settings.py 中配置：

    ITEM_PIPELINES = {
        "tibetanMedResourceSpider.pipelines.JsonWriterPipeline": 300,
    }
"""

import csv
import json
import os
import threading


class JsonWriterPipeline:
    """增量写入 JSON 文件

    每收集 10 条触发一次全量写入（覆盖式），确保数据不丢失。
    可通过 ITEM_PIPELINES 启用，需提供 output_dir 参数：

        ITEM_PIPELINES = {
            "tibetanMedResourceSpider.pipelines.JsonWriterPipeline": 300,
        }
        # 并在 spider 中设置：
        #   custom_settings = {"OUTPUT_DIR": "results/nwipb"}
    """

    def __init__(self, output_dir: str, filename: str = "output.json"):
        self.output_dir = output_dir
        self.filename = filename
        self._items: list[dict] = []
        self._lock = threading.Lock()
        self._filepath: str = ""

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            output_dir=crawler.settings.get("OUTPUT_DIR", "results/nwipb"),
            filename=crawler.settings.get("OUTPUT_FILENAME", "output.json"),
        )

    def open_spider(self, spider):
        os.makedirs(self.output_dir, exist_ok=True)
        self._filepath = os.path.join(self.output_dir, self.filename)
        self._items = []
        spider.logger.info(f"[JsonWriter] 输出: {self._filepath}")

    def process_item(self, item, spider):
        with self._lock:
            self._items.append(dict(item))
            if len(self._items) % 10 == 0:
                self._flush()
        return item

    def close_spider(self, spider):
        if self._items:
            self._flush()
        spider.logger.info(f"[JsonWriter] 写入 {len(self._items)} 条 -> {self._filepath}")

    def _flush(self):
        with open(self._filepath, "w", encoding="utf-8") as f:
            json.dump(self._items, f, ensure_ascii=False, indent=2)


class CsvWriterPipeline:
    """CSV 输出管道

    将嵌套字段展平后写入 CSV，便于在 Excel 中查看。
    """

    def __init__(self, output_dir: str, filename: str = "output.csv"):
        self.output_dir = output_dir
        self.filename = filename
        self._filepath: str = ""
        self._file_handle = None
        self._writer = None
        self._header_written = False

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            output_dir=crawler.settings.get("OUTPUT_DIR", "results/nwipb"),
            filename=crawler.settings.get("OUTPUT_CSV_FILENAME", "output.csv"),
        )

    def open_spider(self, spider):
        os.makedirs(self.output_dir, exist_ok=True)
        self._filepath = os.path.join(self.output_dir, self.filename)
        self._file_handle = open(self._filepath, "w", encoding="utf-8-sig", newline="")
        self._writer = csv.writer(self._file_handle)
        spider.logger.info(f"[CsvWriter] 输出: {self._filepath}")

    def process_item(self, item, spider):
        flat = self._flatten(dict(item))
        if not self._header_written:
            self._writer.writerow(list(flat.keys()))
            self._header_written = True
        self._writer.writerow(list(flat.values()))
        self._file_handle.flush()
        return item

    def close_spider(self, spider):
        if self._file_handle:
            self._file_handle.close()

    @staticmethod
    def _flatten(item: dict, prefix: str = "") -> dict:
        result = {}
        for key, value in item.items():
            full_key = f"{prefix}.{key}" if prefix else key
            if isinstance(value, dict):
                result.update(CsvWriterPipeline._flatten(value, full_key))
            elif isinstance(value, list):
                if value and isinstance(value[0], dict):
                    result[full_key] = json.dumps(value, ensure_ascii=False)
                else:
                    result[full_key] = "; ".join(str(v) for v in value)
            else:
                result[full_key] = value or ""
        return result
