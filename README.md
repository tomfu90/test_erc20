# 🔗 ERC20 + ERC721 智能合约接口自动化测试

基于 **Python + Web3.py + pytest + Allure** 构建的多标准合约全流程测试框架，已完成全量测试并输出可视化报告。

<br>

## 📊 测试成果概览
| 合约类型 | 测试维度         | 用例数量 | 通过率 | 核心覆盖场景                                                                 |
|----------|------------------|----------|--------|------------------------------------------------------------------------------|
| <kbd>ERC20</kbd> | 单元测试 + E2E   | 25个     | 100%   | `transfer`/`approve`/`transferFrom` 全接口+边界场景，覆盖Legacy/EIP-1559交易类型 |
| <kbd>ERC721</kbd> | E2E端到端场景    | 2个      | 100%   | 多Token批量授权链、单Token全生命周期流转，覆盖Legacy/EIP-1559交易类型           |

<br>
<img width="2036" height="1125" alt="合约测试落地" src="https://github.com/user-attachments/assets/11426e94-cdd4-4bb3-951e-e50b35e90d59" />

## 🎯 核心ERC721 E2E场景

### 📦 场景1：多Token + 批量授权 + 权限撤销 + 权限验证
- **操作链路**：
  1. `mint` 铸造多枚NFT
  2. `transferFrom` 转移NFT所有权
  3. `setApprovalForAll` 向指定地址批量授权所有NFT操作权限
  4. 授权方通过 `transferFrom` 转移NFT（验证授权有效）
  5. `setApprovalForAll` 撤销对指定地址的批量授权
  6. 授权方再次尝试 `transferFrom`（触发`ERC721InsufficientApproval`异常，验证无权限）
- **测试目标**：验证批量授权/撤销的权限边界，覆盖异常场景的正确性

<br>

### 🔄 场景2：单Token全生命周期 + 单授权流转
- **操作链路**：
  1. `mint` 铸造单枚NFT
  2. `transferFrom` 转移该NFT的所有权
  3. `approve` 向指定地址授权该NFT的操作权限
  4. 授权方通过 `transferFrom` 转移NFT（验证授权有效）
  5. `burn` 销毁该NFT
- **测试目标**：覆盖单个NFT从创建、转移、授权到销毁的完整生命周期，验证单授权有效性

<br>

## ✨ 已验证核心能力
| 特性                | 说明                                                                 |
|---------------------|----------------------------------------------------------------------|
| 多标准接口全覆盖    | ERC20：`transfer`/`approve`/`transferFrom` 全接口<br>ERC721：`mint`/`transferFrom`/`setApprovalForAll`/`approve`/`burn` 全接口 |
| 双交易类型兼容      | 全量用例适配 <kbd>Legacy</kbd>（传统固定手续费）和 <kbd>EIP-1559</kbd>（新型动态手续费），确保不同交易模式下合约行为一致 |
| 可视化报告能力      | Allure生成可交互报告，包含交易详情、Token追踪、事件日志、断言结果等维度 |
| 自动化校验体系      | ERC20：余额变更、`Transfer`/`Approval` 事件一致性校验<br>ERC721：NFT所有权、授权权限边界、销毁状态校验 |

<br>



