# tibetanMedResourceSpider

藏药材资源数据库爬虫 —— 独立 Scrapy 项目。

采集中国科学院西北高原生物研究所（NWIPB）藏药材资源数据库的结构化数据，包括学名、拉丁名、别名、药用部位、功能主治、形态特征、分布及图片等字段。
https://nwipb.cas.cn/zy/zyc/index.html

## 功能特性

- 纯 HTTP 爬取（无需浏览器自动化，无需登录）
- 使用 BeautifulSoup 解析详情页，提取结构化字段
- 支持分页遍历（15 页，约 300 条记录）
- 解析字段：学名、拉丁名、别名、药材名、药用部位、功能与主治、形态特征、分布、备注、图片列表
- 支持断点续爬、测试模式、并发控制
- JSON / CSV 双管道可选输出

## 项目结构（标准 Scrapy 布局）

```
tibetanMedResourceSpider/
├── scrapy.cfg                                # Scrapy 部署配置（指向 tibetanMedResourceSpider.settings）
├── requirements.txt                          # Python 依赖
├── pyproject.toml                            # 项目元数据 + pytest 配置
├── runner.py                                 # CLI 运行入口（CrawlerProcess 封装）
├── .gitignore
├── README.md
│
├── tibetanMedResourceSpider/                 # 项目 Python 模块
│   ├── __init__.py
│   ├── items.py                              # 数据模型声明 TibetanMedicineItem
│   ├── middlewares.py                        # 中间件（标准模板）
│   ├── pipelines.py                          # JsonWriterPipeline / CsvWriterPipeline
│   ├── settings.py                           # Scrapy 全局配置
│   └── spiders/                              # 爬虫目录
│       ├── __init__.py
│       ├── models.py                         # MedicineRecord / MedicineImage 数据模型
│       └── tibetan_medicine.py               # NwipbTibetanMedicineSpider 主爬虫
│
├── tests/
│   ├── __init__.py
│   └── test_nwipb_pipeline.py                # Pipeline + 数据模型单元测试
│
├── results/                                  # [生成] 爬虫输出（.gitignore 忽略）
│   ├── nwipb_<时间戳>.json                    #   JSON 数据
│   └── .scrapy_jobs/                          #   断点续爬状态
│
└── log/                                      # [生成] 运行日志（.gitignore 忽略）
```

## 环境准备

### 1. 安装依赖

```bash
# 建议使用 Python >= 3.12
pip install -r requirements.txt
```

### 2. 安装测试依赖（可选）

```bash
pip install pytest
```

## 使用方法

所有命令需在项目根目录执行（确保 `results/`、`log/` 等相对路径生效）。

### 运行爬虫

#### 测试模式（推荐先运行，验证流程是否正常）

```bash
# 只爬取第一页（首页），快速验证检索/解析是否正常
python -m runner --test
```

#### 完整爬取（生产使用）

```bash
# 完整爬取所有分页（15 页），输出到 results/
python -m runner
```

#### 自定义输出与并发

```bash
# 指定输出目录（默认: ./results）
python -m runner -o D:\\output

# 调整并发请求数（默认: 5）
python -m runner -c 8

# 组合使用：测试模式 + 指定输出 + 高并发
python -m runner --test -o D:\\output -c 8
```

#### 标准 Scrapy 命令（也可使用）

```bash
scrapy crawl nwipb              # 运行爬虫（使用 settings.py 默认配置）
scrapy list                     # 列出项目所有爬虫
```

### CLI 参数说明

| 参数                | 说明                                          |
| ------------------- | --------------------------------------------- |
| `--list`            | 列出所有可用爬虫                               |
| `-o, --output PATH` | 输出目录（默认: `./results`）                |
| `-c, --concurrency` | 并发请求数（默认: 5）                          |
| `--no-resume`       | 不从断点续爬，删除进度重新开始                 |
| `--test`            | 测试模式，只爬取第一页                         |

## 输出说明

- **藏药材数据 JSON**：`results/nwipb_<时间戳>.json`
  - 包含所有字段的完整记录列表
- **日志**：`log/nwipb_<时间戳>.log`
- **断点续爬状态**：`results/.scrapy_jobs/`

### 数据字段

| 字段                          | 说明                           |
| ----------------------------- | ------------------------------ |
| `scientific_name`             | 学名                           |
| `latin_name`                  | 拉丁名                         |
| `aliases`                     | 别名列表                       |
| `medicine_name`               | 药材名                         |
| `medicinal_parts`             | 药用部位列表                   |
| `functions_and_indications`   | 功能与主治                     |
| `morphological_characteristics` | 形态特征                     |
| `distribution`                | 分布                           |
| `notes`                       | 备注                           |
| `images`                      | 图片列表 `[{url, alt}, ...]`  |
| `source_url`                  | 详情页 URL                     |
| `crawled_at`                  | 爬取时间（UTC ISO 格式）       |

## 编程使用

```python
from runner import run_spider

run_spider(
    spider_name="nwipb",
    output_dir="./results",
    concurrency=5,
    resume=True,
    test_mode=False,
)
```

## 测试

```bash
pytest
```
