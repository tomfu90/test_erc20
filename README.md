🔗 ERC20 + ERC721 智能合约接口自动化测试
基于 Python + Web3.py + pytest + Allure 构建的多标准合约全流程测试框架，已完成全量测试并生成可视化报告。
📊 测试成果概览（Allure 报告数据）
合约类型	测试维度	用例数量	通过率	核心覆盖场景
ERC20	单元测试 + E2E	25 个	100%	transfer/approve/transferFrom 全接口 + 边界场景
ERC721	E2E 端到端场景	2 个	100%	多 Token 批量授权链、单 Token 全生命周期流转
🎯 已覆盖的核心 ERC721 E2E 场景
场景 1：多 Token + 批量授权（setApprovalForAll）+ 权限撤销 + 权限验证
操作链：mint（多枚NFT）→ transferFrom（转移NFT）→ setApprovalForAll（批量授权）→ approved transferFrom（授权方转账）→ setApprovalForAll（批量撤销）→ approved transferFrom（验证无权限）
测试目标：验证批量授权 / 撤销的权限边界，覆盖ERC721InsufficientApproval异常场景
场景 2：单 Token 全生命周期 + 单授权流转
操作链：mint（单枚NFT）→ transferFrom（所有权转移）→ approve（单个授权）→ approved transferFrom（授权方转账）→ burn（销毁NFT）
测试目标：覆盖单个 NFT 从创建到销毁的全流程，验证单授权的有效性
✨ 核心能力（已验证）
特性	说明
多标准接口全覆盖	ERC20：transfer/approve/transferFrom 等标准接口；
ERC721：mint/transferFrom/setApprovalForAll/approve/burn 全接口
双交易类型兼容	适配 EIP-1559（新型手续费）+ Legacy（传统格式）两种交易模式
可视化报告能力	Allure 生成含交易详情、Token 追踪、事件日志、断言结果的报告，支持场景步骤拆解
自动化校验体系	ERC20：余额变更、Transfer/Approval 事件一致性；
ERC721：NFT 所有权、授权权限边界、销毁状态校验

<img width="2036" height="1125" alt="合约测试落地" src="https://github.com/user-attachments/assets/8f099bb7-0b87-48b2-920e-249f60fc5551" />

