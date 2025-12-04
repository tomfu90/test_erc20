ERC20 智能合约自动化测试项目
基于 Python + Web3.py + pytest + Allure 实现的 ERC20 代币自动化测试框架，支持 EIP-1559 和 Legacy 两种交易类型，适配 Hardhat 本地测试节点与以太坊测试网，可生成可视化测试报告。
功能特性
全覆盖核心接口：支持 transfer、approve、transferFrom 等 ERC20 标准接口测试
双交易类型支持：同时兼容 EIP-1559（新型手续费机制）和 Legacy（传统交易）模式
多环境适配：无缝对接 Hardhat 本地节点（默认 ChainID: 31337）与以太坊 Sepolia 等测试网
可视化报告：集成 Allure 生成测试报告，包含交易详情、日志解析、断言结果
自动化校验：自动校验交易回执状态、余额变更、Transfer 事件日志
项目结构
plaintext
eth_test/
├── tests/                  # 测试用例目录
│   ├── e2e/                # 端到端测试（部署合约+链上交易）
│   │   ├── test_erc20_approve_eip_1559.py
│   │   ├── test_erc20_transferfrom_legacy.py
│   │   └── test_eth_legacy.py
│   └── unit/               # 单元测试（合约方法逻辑校验）
│       ├── test_erc20_eip1559_transfer_unit.py
│       └── test_erc20_eip1559_transferfrom_unit.py
├── libs/                   # 工具类目录（如合约ABI加载、YAML用例读取）
├── yaml_case/              # YAML 测试用例数据（账号、金额、参数配置）
├── pytest.ini              # pytest 配置文件
├── run_test.sh             # 测试运行脚本
├── requirements.txt        # 项目依赖清单
└── README.md               # 项目说明文档
环境准备
1. 克隆仓库
bash
运行
git clone https://github.com/tomfu90/test_erc20.git
cd test_erc20
2. 安装依赖
bash
运行
# 创建虚拟环境
python -m venv .venv

# 激活虚拟环境
# Mac/Linux
source .venv/bin/activate
# Windows
.venv\Scripts\activate

# 安装依赖包
pip install -r requirements.txt
3. 安装 Allure 报告工具
参考 Allure 官方文档 完成安装，用于生成可视化测试报告。
4. 配置 Hardhat 本地节点
安装 Node.js 和 Hardhat
初始化 Hardhat 项目并启动本地节点：
bash
运行
npx hardhat node
确保测试代码中 chainId 配置为 31337（Hardhat 本地节点默认值）
快速开始
运行测试
执行项目根目录下的测试脚本：
bash
运行
./run_test.sh
查看 Allure 报告
bash
运行
allure serve report/allure-results
报告将自动在浏览器中打开，展示测试通过率、用例详情、交易日志等信息。
测试用例编写规范
用例数据管理：测试参数（账号私钥、转账金额、合约地址）统一写在 yaml_case/ 目录下的 YAML 文件中
Allure 报告增强：通过 allure.step 和 allure.attach 添加测试步骤和交易详情（注意：字典需通过 json.dumps 转为字符串后再附加）
断言校验要点：
交易回执 status 等于 1（交易成功）
转账前后余额变更符合预期
Transfer 事件日志中的 from、to、value 参数正确
注意事项
私钥安全：请勿将包含真实私钥的 YAML 文件提交到仓库，建议通过 .env 文件管理敏感信息，并添加到 .gitignore
Gas 费配置：EIP-1559 交易需合理设置 maxPriorityFeePerGas 和 maxFeePerGas，避免交易失败
分支管理：日常开发请基于 dev 分支提交代码，合并到 main 分支前需通过全部测试
贡献指南
欢迎提交 Issue 和 Pull Request，贡献代码请遵循以下规范：
新增功能需配套编写对应的测试用例
确保代码通过 pylint 等代码检查工具校验
提交信息请遵循 type: description 格式（如 feat: 新增 ERC20 allowance 校验）

The project includes native support for TypeScript, Hardhat scripts, tasks, and support for Solidity compilation and tests.
<img width="2366" height="1062" alt="image" src="https://github.com/user-attachments/assets/853f0e97-5061-4477-b039-95e41ae65d39" />
