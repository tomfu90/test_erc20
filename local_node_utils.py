import web3
from eth_account import Account
from web3 import Web3

# 连接本地节点
w3 = Web3(Web3.HTTPProvider("http://127.0.0.1:8545"))
assert w3.is_connected(), "请先运行 npx hardhat node"

# 🪙 标准 ERC20 ABI（仅含 5 个核心方法，无参数名，兼容所有实现）
ERC20_ABI = [
    # --- 代币元信息 ---
    {
        "inputs": [],
        "name": "name",
        "outputs": [{"type": "string"}],
        "stateMutability": "view",
        "type": "function"
    },
    {
        "inputs": [],
        "name": "symbol",
        "outputs": [{"type": "string"}],
        "stateMutability": "view",
        "type": "function"
    },
    {
        "inputs": [],
        "name": "decimals",
        "outputs": [{"type": "uint8"}],
        "stateMutability": "view",
        "type": "function"
    },
    # --- 核心功能 ---
    {
        "inputs": [{"type": "address"}],
        "name": "balanceOf",
        "outputs": [{"type": "uint256"}],
        "stateMutability": "view",
        "type": "function"
    },
    {
        "inputs": [{"type": "address"}, {"type": "uint256"}],
        "name": "transfer",
        "outputs": [{"type": "bool"}],
        "stateMutability": "nonpayable",
        "type": "function"
    },
    {
        "inputs": [{"type": "address"}, {"type": "uint256"}],
        "name": "approve",
        "outputs": [{"type": "bool"}],
        "stateMutability": "nonpayable",
        "type": "function"
    },
    {
        "inputs": [{"type": "address"}, {"type": "address"}, {"type": "uint256"}],
        "name": "transferFrom",
        "outputs": [{"type": "bool"}],
        "stateMutability": "nonpayable",
        "type": "function"
    },
    {
        "inputs": [{"type": "address"}, {"type": "address"}],
        "name": "allowance",
        "outputs": [{"type": "uint256"}],
        "stateMutability": "view",
        "type": "function"
    },
 # --- ERC20标准事件（补充部分）---
    {
        "anonymous": False,
        "inputs": [
            {"indexed": True, "type": "address", "name": "from"},
            {"indexed": True, "type": "address", "name": "to"},
            {"indexed": False, "type": "uint256", "name": "value"}
        ],
        "name": "Transfer",
        "type": "event"
    },
    {
        "anonymous": False,
        "inputs": [
            {"indexed": True, "type": "address", "name": "owner"},
            {"indexed": True, "type": "address", "name": "spender"},
            {"indexed": False, "type": "uint256", "name": "value"}
        ],
        "name": "Approval",
        "type": "event"
    }
]
# 合约地址
TOKEN_ADDR = "0x5FbDB2315678afecb367f032d93F642f64180aa3"
token = w3.eth.contract(address=Web3.to_checksum_address(TOKEN_ADDR), abi=ERC20_ABI)

if __name__ == "__main__":
    # 获取代币信息（可选）
    #合约代币精度
    decimals = token.functions.decimals().call()  # 通常是 18
    #合约名字
    name = token.functions.name().call()
    #合约符号
    symbol = token.functions.symbol().call()

    sender_pk="0x92db14e403b83dfe3df233f83dfa3a0d7096f21ca9b0d6d6b8d88b2b4ec1564e"
    sender = Account.from_key(sender_pk)
    balance_eth = w3.eth.get_balance(sender.address)
    print(balance_eth)

