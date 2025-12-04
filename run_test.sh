#!/bin/bash
# run_test.sh

cd "$(dirname "$0")"

# 激活虚拟环境（注意：Jenkins 脚本已创建 .venv）
source .venv/bin/activate

# 定义目录
RESULT_DIR="./report/allure-results"
REPORT_DIR="./report/allure-report"

# 确保目录存在
mkdir -p "$RESULT_DIR"
mkdir -p "$REPORT_DIR"

# 执行测试，生成 allure-results（供 Jenkins 使用）
pytest tests --alluredir="$RESULT_DIR" "$@"

# 生成 HTML 报告（本地可直接打开查看）
allure generate "$RESULT_DIR" -o "$REPORT_DIR" --clean

# 提示报告路径
echo "======================================"
echo "✅ Allure 测试报告已生成："
echo "📊 HTML 报告路径：$(realpath "$REPORT_DIR/index.html")"
echo "📈 原始数据路径：$(realpath "$RESULT_DIR")"
echo "======================================"