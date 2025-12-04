# 🔗 ERC20 智能合约接口自动化测试

基于 **Python + Web3.py + pytest + Allure** 构建的 ERC20 代币全流程测试框架，支持 EIP-1559/Legacy 交易，适配本地节点与公链测试网，生成可视化测试报告。


## ✨ 核心能力
| 特性                | 说明                                                                 |
|---------------------|----------------------------------------------------------------------|
| 接口全覆盖          | 支持 `transfer`/`approve`/`transferFrom` 等 ERC20 标准接口测试       |
| 双交易类型          | 兼容 EIP-1559（新型手续费）+ Legacy（传统格式）两种交易模式          |
| 多环境适配          | 支持 Hardhat 本地节点（ChainID:31337）、Sepolia 等以太坊测试网       |
| 可视化报告          | Allure 生成含交易详情、日志解析、断言结果的可视化报告                |
| 自动化校验          | 自动验证交易状态、余额变更、Transfer 事件日志一致性                  |

<img width="2491" height="1162" alt="image" src="https://github.com/user-attachments/assets/ae40d151-8882-4e79-a9dc-db477c791934" />
