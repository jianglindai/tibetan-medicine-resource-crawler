"""NWIPB 藏药材资源数据库爬虫

目标站点: https://nwipb.cas.cn/zy/zyc/index.html
数据: 约 300 条藏药材记录 (15 页 x ~20 条/页)
"""

import re
from datetime import datetime, timezone
from urllib.parse import urljoin

import scrapy
from bs4 import BeautifulSoup

from .models import MedicineImage, MedicineRecord

BASE_URL = "https://nwipb.cas.cn"
LIST_BASE = f"{BASE_URL}/zy/zyc"


class NwipbTibetanMedicineSpider(scrapy.Spider):
    """藏药材资源数据库爬虫

    使用方式:
        scrapy crawl nwipb
        python -m runner nwipb
    """

    name = "nwipb"
    start_urls = [f"{LIST_BASE}/index.html"]

    custom_settings = {
        "CONCURRENT_REQUESTS": 5,
        "DOWNLOAD_DELAY": 0.3,
        "RANDOMIZE_DOWNLOAD_DELAY": True,
        "RETRY_TIMES": 3,
    }

    def __init__(self, test_mode=False, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.test_mode = test_mode

    def parse(self, response):
        """解析列表页，提取详情页 URL，并生成后续分页请求"""
        yield from self._parse_list(response)

        if not self.test_mode:
            for i in range(1, 15):
                yield scrapy.Request(f"{LIST_BASE}/index_{i}.html", callback=self._parse_list)

    def _parse_list(self, response):
        """从列表页提取详情页 URL"""
        soup = BeautifulSoup(response.text, "html.parser")
        tbody = soup.find("tbody", id="content")
        if not tbody:
            self.logger.warning(f"列表页未找到 tbody#content: {response.url}")
            return

        for a_tag in tbody.find_all("a", href=True):
            abs_url = urljoin(LIST_BASE + "/", a_tag["href"].lstrip("./"))
            yield scrapy.Request(abs_url, callback=self.parse_detail)

    def parse_detail(self, response):
        """从详情页提取结构化数据"""
        soup = BeautifulSoup(response.text, "html.parser")
        record = MedicineRecord(
            source_url=response.url,
            crawled_at=datetime.now(timezone.utc).isoformat(),
        )

        # 基本信息
        intro_div = soup.select_one(".userMessage-top .introduceList")
        if intro_div:
            for p_tag in intro_div.find_all("p", class_="list"):
                text = self._clean_text(p_tag.get_text())
                if "学名" in text:
                    record.scientific_name = text.replace("学名：", "").replace("学名:", "").strip()
                elif "拉丁名" in text:
                    record.latin_name = text.replace("拉丁名：", "").replace("拉丁名:", "").strip()
                elif "别名" in text:
                    aliases_text = text.replace("别名：", "").replace("别名:", "").strip()
                    if aliases_text:
                        record.aliases = [a.strip() for a in aliases_text.replace("、", "，").split("，") if a.strip()]
                elif "药材名" in text:
                    record.medicine_name = text.replace("药材名：", "").replace("药材名:", "").strip()
                elif "药用部位" in text:
                    parts_text = text.replace("药用部位：", "").replace("药用部位:", "").strip()
                    if parts_text:
                        record.medicinal_parts = [
                            p.strip() for p in parts_text.replace("、", "，").split("，") if p.strip()
                        ]

        # 备用标题
        title_elem = soup.select_one(".userMessage-top .title .name")
        if title_elem and not record.scientific_name:
            record.scientific_name = self._clean_text(title_elem.get_text())

        # 详细描述
        section_map = {
            "b1": "functions_and_indications",
            "b2": "morphological_characteristics",
            "b3": "distribution",
            "b5": "notes",
        }
        for elem_id, field_name in section_map.items():
            div = soup.find("div", id=elem_id)
            if div:
                text = self._clean_text(div.get_text())
                if text:
                    setattr(record, field_name, text)

        # 图片
        images_div = soup.find("div", id="b4")
        if images_div:
            for img_tag in images_div.find_all("img"):
                src = img_tag.get("src") or img_tag.get("OLDSRC", "")
                if src:
                    img_url = urljoin(response.url, src)
                    record.images.append(
                        MedicineImage(url=img_url, alt=img_tag.get("alt", "").strip())
                    )

        yield record.to_dict()

    @staticmethod
    def _clean_text(text: str) -> str:
        if not text:
            return ""
        return re.sub(r"\s+", " ", text).strip()
