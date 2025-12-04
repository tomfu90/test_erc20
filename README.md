ERC20 智能合约自动化测试项目
基于 Python + Web3.py + pytest + Allure 构建的 ERC20 代币自动化测试框架，支持 EIP-1559 和 Legacy 两种交易类型，无缝适配 Hardhat 本地测试节点与以太坊公共测试网，可生成可视化、可追溯的测试报告。
✨ 核心特性
接口全覆盖：深度覆盖 transfer、approve、transferFrom 等 ERC20 标准核心接口
双交易模式：同时兼容 EIP-1559 新型手续费机制与 Legacy 传统交易格式
多环境适配：支持 Hardhat 本地节点（默认 ChainID: 31337）、Sepolia 等以太坊测试网
可视化报告：集成 Allure 生成测试报告，包含交易详情、日志解析、断言结果全链路展示
自动化校验：自动校验交易回执状态、账户余额变更、Transfer 事件日志参数一致性
📁 项目结构
plaintext
eth_test/
├── tests/                  # 测试用例主目录
│   ├── e2e/                # 端到端测试：部署合约+链上完整交易流程
│   │   ├── test_erc20_approve_eip_1559.py
│   │   ├── test_erc20_transferfrom_legacy.py
│   │   └── test_eth_legacy.py
│   └── unit/               # 单元测试：合约方法逻辑独立校验
│       ├── test_erc20_eip1559_transfer_unit.py
│       └── test_erc20_eip1559_transferfrom_unit.py
├── libs/                   # 工具类目录：ABI加载、YAML用例读取、链上数据解析
├── yaml_case/              # YAML 测试用例数据：账号、金额、交易参数配置
├── pytest.ini              # pytest 配置文件：报告路径、用例分组规则
├── run_test.sh             # 一键运行测试脚本
├── requirements.txt        # 项目依赖清单
└── README.md               # 项目说明文档
🚀 快速开始
1. 克隆仓库
bash
运行
git clone https://github.com/tomfu90/test_erc20.git
cd test_erc20
2. 环境配置
2.1 安装 Python 依赖
bash
运行
# 创建并激活虚拟环境
python -m venv .venv

# Mac/Linux 激活命令
source .venv/bin/activate
# Windows 激活命令
.venv\Scripts\activate

# 安装依赖包
pip install -r requirements.txt
2.2 安装 Allure 报告工具
参考 Allure 官方文档 完成安装，用于生成可视化测试报告。
2.3 启动 Hardhat 本地节点
bash
运行
# 初始化 Hardhat 项目（首次使用）
npx hardhat init

# 启动本地测试节点
npx hardhat node
注意：确保测试代码中 chainId 配置为 31337（Hardhat 本地节点默认值）
3. 运行测试
执行项目根目录下的一键测试脚本：
bash
运行
./run_test.sh
4. 查看测试报告
bash
运行
allure serve report/allure-results
命令执行后，浏览器将自动打开报告页面，展示测试通过率、用例执行详情、交易日志等信息。
📝 用例编写规范
用例数据解耦：测试参数（私钥、转账金额、合约地址）统一维护在 yaml_case/ 目录的 YAML 文件中
报告增强技巧：通过 allure.step 划分测试步骤，allure.attach 附加交易信息；字典需通过 json.dumps 转为字符串后再附加
核心断言要点
交易回执 status 必须等于 1（交易上链成功）
转账后账户余额 = 转账前余额 ± 转账金额（需换算代币精度）
Transfer 事件日志的 from、to、value 与入参完全一致
⚠️ 注意事项
私钥安全：严禁将含真实私钥的 YAML 文件提交至仓库，建议通过 .env 文件管理敏感信息，并将 .env 加入 .gitignore
Gas 费优化：EIP-1559 交易需合理配置 maxPriorityFeePerGas 和 maxFeePerGas，避免因 Gas 费不足导致交易失败
分支管理规范：日常开发基于 dev 分支提交代码，合并 main 分支前需通过全部测试用例校验
🤝 贡献指南
欢迎提交 Issue 和 Pull Request，贡献代码请遵循以下规范：
新增功能需配套编写对应的单元测试与端到端测试用例
代码需通过 pylint 等代码规范检查工具校验
提交信息遵循 type: description 格式（示例：feat: 新增 ERC20 allowance 余额校验）

The project includes native support for TypeScript, Hardhat scripts, tasks, and support for Solidity compilation and tests.
<img width="2366" height="1062" alt="image" src="https://github.com/user-attachments/assets/853f0e97-5061-4477-b039-95e41ae65d39" />
