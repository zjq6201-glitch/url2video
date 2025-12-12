# 测试说明

这个目录包含了项目的所有测试脚本。

## 测试文件

- `test_env.py` - 环境检查（Python版本、依赖包、环境变量）
- `test_scraper.py` - 网页抓取模块测试
- `test_ai_director.py` - AI脚本生成模块测试
- `test_video_engine.py` - 视频生成模块测试
- `run_all_tests.py` - 运行所有测试的脚本

## 运行测试

### 运行单个测试

```bash
# 从项目根目录运行
python tests/test_scraper.py

# 或者从 tests 目录运行
cd tests
python test_scraper.py
```

### 运行所有测试

```bash
# 从项目根目录运行
python tests/run_all_tests.py

# 或者从 tests 目录运行
cd tests
python run_all_tests.py
```

## 测试顺序

建议按以下顺序运行测试：

1. **test_env.py** - 首先检查环境配置
2. **test_scraper.py** - 测试网页抓取功能
3. **test_ai_director.py** - 测试AI脚本生成
4. **test_video_engine.py** - 测试视频生成（最耗时）

## 注意事项

- 确保已安装所有依赖：`pip install -r requirements.txt`
- 确保已配置环境变量（`.env` 文件）：
  - `SCRAPERAPI_KEY`
  - `DEEPSEEK_API_KEY`
- 视频生成测试可能需要较长时间（1-2分钟）