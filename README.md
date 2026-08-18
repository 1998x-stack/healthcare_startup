# healthcare_startup

医疗数据采集 + 基于 ChatGPT 的医疗咨询微信小程序。Python 侧负责从公开医疗站点
抓取医院/科室/医生、药品、医患问答等数据；小程序侧 (`MedGPT/`) 提供对话式医疗
咨询服务。

## 项目结构

```
healthcare_startup
├── scrapers/              # Python 爬虫包（工厂模式）
│   ├── __init__.py        # 公开 API: create_scraper, ScraperFactory
│   ├── base.py            # BaseScraper：共享流水线 + 多进程编排
│   ├── parsers.py         # BaseParser + Hospital/Medicine/QA 解析器 + 注册表
│   ├── scrapers.py        # HospitalScraper / MedicineScraper / QAScraper
│   ├── factory.py         # ScraperFactory.create(site) 工厂
│   └── urls.py            # 各站点 URL 构建
├── libs/
│   ├── utils.py           # get_soup / save_js / save_csv（logger 可选）
│   ├── log.py             # 日志系统
│   └── tools/correct_name.py   # 乱码修复工具（--dry-run 安全模式）
├── config.py              # 集中配置（路径、进程数、站点名）
├── run.py                 # 命令行入口：python run.py hospital|medicine|qa
├── MedGPT/                # 微信小程序（注册登录/问答/聊天/推荐/档案）
├── docs/                  # 文档（见下）
├── data/                  # 采集数据输出
└── tests/                 # pytest（离线，使用 fixture）
```

## 安装

```bash
conda create -n health
conda activate health
pip install -r requirement.txt
```

## 运行爬虫（工厂模式）

```bash
python run.py hospital [--processes 8]
python run.py medicine [--processes 8] [--count 100000]
python run.py qa        [--processes 8] [--count 1000]
```

架构说明：`ScraperFactory.create(site)` 返回一个绑定对应解析器的具体 Scraper；
三者共享 `BaseScraper` 的流水线与 `multiprocessing.JoinableQueue` 多进程编排
（避免 `_thread.lock` 崩溃）。具体设计见 `docs/architecture.md`。

## 数据源（Url List）

1. 医学百科：http://www.a-hospital.com/w/%E9%A6%96%E9%A1%B5 （全国医院列表 / 药品百科）
2. 健康界：https://www.cn-healthcare.com/ ；医院排行榜 http://rank.cn-healthcare.com/
3. 益药：http://www.xinyao.com.cn/
4. 健康到家（药品）：https://www.jianke.com/
5. 药品网：http://y.wksc.com/
6. 疾病大全：http://y.wksc.com/jbdq.html
7. 疾病百科：https://www.youlai.cn/dise/
8. 120ask：https://www.120ask.com/
9. 药源网：https://www.yaopinnet.com/

## 数据

| 站点(scraper) | 输出目录 | 说明 |
| --- | --- | --- |
| hospital | `data/hospital/` | 北京医院 + 科室 + 医生信息 |
| medicine | `data/medician/` | 药品、功能主治、价格、说明书、相关药品 |
| qa | `data/ques_ans/` | 医患问答 + 医生简介 |

种子数据：`yiyuandiqu-beijing.csv` / `beijing_hospital.json`（北京市医院清单）。

## 测试

```bash
pytest tests/ -v
```

全部离线运行（不含真实网络请求）：工厂、URL 构造、BaseScraper、解析器（基于
fixture HTML）、CLI，以及端到端多进程流水线冒烟（`scripts/smoke_integration.py`）。

## 已知问题 / 调试

- **乱码**：`data/hospital/东城/北京协和医院/` 下 55 个科室目录名因旧工具多次转换
  已无法用启发式恢复（重命名会误改数据），故保留为 `renamed-*`。请勿手动批量重命名。
  可用 `python -m libs.tools.correct_name <target> --dry-run` 预览可恢复项。
- 旧版顶层单文件爬虫（`hospital_info.py`/`medician.py`/`ques_ans.py`）仍保留但已**弃用**，
  其逻辑已迁移到 `scrapers/` 包的解析器中；重复的 `_copy.py` 与根目录 `log.py` 已删除。
  新开发统一以 `scrapers/` 包 + `run.py` 为准。

## 目标 / 成本 / TODO

平台思维建立患者信息档案（P0）、体检报告解读（P0）、数据飞轮（P0）；次优：帮
患者匹配医院/科室/医生（P1），与 ChatGPT 对话问答（P2），可靠性评价（P3），体检
报告生成（P3），X 片补充信息（P3）。成本假设与更多细节见 `MedGPT.md` / `docs/`。