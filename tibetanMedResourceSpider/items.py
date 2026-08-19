"""藏药材资源数据模型声明

爬虫当前直接 yield dict（由 MedicineRecord.to_dict() 生成），
本 Item 用于声明数据结构，便于后续扩展与校验。
"""

import scrapy


class TibetanMedicineItem(scrapy.Item):
    """藏药材条目数据模型

    字段对应 NwipbTibetanMedicineSpider.parse_detail 解析输出的字段。
    """

    # 基本信息
    scientific_name = scrapy.Field()  # 学名
    latin_name = scrapy.Field()  # 拉丁名
    aliases = scrapy.Field()  # 别名列表
    medicine_name = scrapy.Field()  # 药材名
    medicinal_parts = scrapy.Field()  # 药用部位列表

    # 详细描述
    functions_and_indications = scrapy.Field()  # 功能与主治
    morphological_characteristics = scrapy.Field()  # 形态特征
    distribution = scrapy.Field()  # 分布
    notes = scrapy.Field()  # 备注

    # 图片
    images = scrapy.Field()  # [{url, alt, local_path}, ...]

    # 来源信息
    source_url = scrapy.Field()
    crawled_at = scrapy.Field()
