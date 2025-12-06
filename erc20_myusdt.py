import web3
from eth_account import Account
from web3 import Web3

# 连接本地节点
w3 = Web3(Web3.HTTPProvider("http://127.0.0.1:8545"))
assert w3.is_connected(), "请先运行 npx hardhat node"

# 🪙 标准 ERC20 ABI（仅含 5 个核心方法 + 事件，兼容所有实现）
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
    # --- ERC20标准事件 ---
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
TOKEN_ADDR = "0x0165878A594ca255338adfa4d48449f69242Eb8F"
token = w3.eth.contract(address=Web3.to_checksum_address(TOKEN_ADDR), abi=ERC20_ABI)