"""
Scrapy 爬虫运行入口 —— 藏药材资源爬虫
time: 2026-08-19
author：大江
"""


from __future__ import annotations

import argparse
import importlib
import os
import shutil
import sys
from datetime import datetime, timezone

# 确保项目根目录在 sys.path 中（runner.py 位于项目根目录）
_root = os.path.dirname(os.path.abspath(__file__))
if _root not in sys.path:
    sys.path.insert(0, _root)

# 显式指定 Scrapy 设置模块
os.environ.setdefault("SCRAPY_SETTINGS_MODULE", "tibetanMedResourceSpider.settings")

from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

SPIDER_REGISTRY: dict[str, str] = {
    "nwipb": "tibetanMedResourceSpider.spiders.tibetan_medicine.NwipbTibetanMedicineSpider",
}


def _import_from_string(dotted_path: str):
    """从字符串路径导入类"""
    module_path, attr_name = dotted_path.rsplit(".", 1)
    module = importlib.import_module(module_path)
    return getattr(module, attr_name)


def run_spider(
    spider_name: str = "nwipb",
    output_dir: str = "",
    concurrency: int = 5,
    resume: bool = True,
    test_mode: bool = False,
    **kwargs,
) -> None:
    """运行指定爬虫

    Args:
        spider_name: 爬虫名称 (SPIDER_REGISTRY 中的 key，默认 nwipb)
        output_dir: 输出目录
        concurrency: 并发数
        resume: 是否从断点续爬
        test_mode: 测试模式，只爬取第一页
    """
    if spider_name not in SPIDER_REGISTRY:
        available = list(SPIDER_REGISTRY.keys())
        raise ValueError(f"未知爬虫 '{spider_name}'，可用爬虫: {available}")

    if not output_dir:
        output_dir = os.path.join(os.getcwd(), "results")

    os.makedirs(output_dir, exist_ok=True)

    ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    feed_uri = os.path.join(output_dir, f"{spider_name}_{ts}.json")
    job_dir = os.path.join(output_dir, ".scrapy_jobs")

    # 断点续爬
    if not resume and os.path.exists(job_dir):
        shutil.rmtree(job_dir)

    settings = get_project_settings()
    settings.set(
        "FEEDS",
        {
            feed_uri: {
                "format": "json",
                "encoding": "utf-8",
                "indent": 2,
                "ensure_ascii": False,
            }
        },
    )
    settings.set("JOBDIR", job_dir)
    settings.set("CONCURRENT_REQUESTS", concurrency)
    settings.set("LOG_LEVEL", "INFO")

    # 日志文件输出到 log/{spider_name}_{timestamp}.log
    log_dir = os.path.join(os.getcwd(), "log")
    os.makedirs(log_dir, exist_ok=True)
    log_file = os.path.join(log_dir, f"{spider_name}_{ts}.log")
    settings.set("LOG_FILE", log_file)

    process = CrawlerProcess(settings)
    spider_cls = _import_from_string(SPIDER_REGISTRY[spider_name])
    process.crawl(spider_cls, test_mode=test_mode)
    process.start()


def main():
    parser = argparse.ArgumentParser(description="藏药材资源 Scrapy 爬虫")
    parser.add_argument(
        "spider",
        nargs="?",
        default="nwipb",
        help=f"爬虫名称: {', '.join(SPIDER_REGISTRY.keys())}（默认: nwipb）",
    )
    parser.add_argument(
        "-o",
        "--output",
        default="",
        help="输出目录 (默认: ./results)",
    )
    parser.add_argument(
        "-c",
        "--concurrency",
        type=int,
        default=5,
        help="并发数 (默认: 5)",
    )
    parser.add_argument(
        "--no-resume",
        action="store_true",
        help="不从断点续爬，重新爬取",
    )
    parser.add_argument(
        "--list",
        action="store_true",
        help="列出所有可用爬虫",
    )
    parser.add_argument(
        "--test",
        action="store_true",
        help="测试模式：只爬取第一页",
    )

    args = parser.parse_args()

    if args.list:
        print("可用爬虫:")
        for name, path in SPIDER_REGISTRY.items():
            print(f"  {name:30s} -> {path}")
        return

    if not args.spider:
        parser.print_help()
        return

    run_spider(
        spider_name=args.spider,
        output_dir=args.output,
        concurrency=args.concurrency,
        resume=not args.no_resume,
        test_mode=args.test,
    )


if __name__ == "__main__":
    main()
