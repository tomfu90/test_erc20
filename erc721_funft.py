# erc721_funft.py
# coding = utf-8
# author =fufu
import web3
from eth_account import Account
from web3 import Web3
from libs.utils import  parse_erc721_error
from web3.exceptions import Web3RPCError
# 连接本地 Hardhat 节点
w3 = Web3(Web3.HTTPProvider("http://127.0.0.1:8545"))
assert w3.is_connected(), "节点连接失败！请先启动 Hardhat 节点"

# -------------------------- 分类 JSON 格式 ERC721 ABI --------------------------
ERC721_ABI = [
    # ========== 读方法 ==========
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
        "inputs": [{"type": "address"}],
        "name": "balanceOf",
        "outputs": [{"type": "uint256"}],
        "stateMutability": "view",
        "type": "function"
    },
    {
        "inputs": [{"type": "uint256"}],
        "name": "ownerOf",
        "outputs": [{"type": "address"}],
        "stateMutability": "view",
        "type": "function"
    },
    {
        "inputs": [{"type": "uint256"}],
        "name": "getApproved",
        "outputs": [{"type": "address"}],
        "stateMutability": "view",
        "type": "function"
    },
    {
        "inputs": [{"type": "address"}, {"type": "address"}],
        "name": "isApprovedForAll",
        "outputs": [{"type": "bool"}],
        "stateMutability": "view",
        "type": "function"
    },
    {
        "inputs": [{"type": "uint256"}],
        "name": "meta",
        "outputs": [{"type": "string"}],
        "stateMutability": "view",
        "type": "function"
    },
    # ========== 写方法 ==========
    {
        "inputs": [
            {"type": "address"},
            {"type": "uint256"},
            {"type": "string"}
        ],
        "name": "mint",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function"
    },
    {
        "inputs": [
            {"type": "address"},
            {"type": "uint256"},
            {"type": "string"}
        ],
        "name": "safeMint",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function"
    },
    {
        "inputs": [{"type": "uint256"}],
        "name": "burn",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function"
    },
    {
        "inputs": [{"type": "address"}, {"type": "uint256"}],
        "name": "approve",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function"
    },
    {
        "inputs": [{"type": "address"}, {"type": "bool"}],
        "name": "setApprovalForAll",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function"
    },
    {
    "inputs": [
        {"type": "address", "name": "to"},
        {"type": "uint256", "name": "tokenId"}
    ],
    "name": "transfer",
    "outputs": [],
    "stateMutability": "nonpayable",
    "type": "function"
    },
    {
        "inputs": [{"type": "address"}, {"type": "address"}, {"type": "uint256"}],
        "name": "transferFrom",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function"
    },
    # ========== 事件 ==========
    {
        "anonymous": False,
        "inputs": [
            {"indexed": True, "type": "address", "name": "from"},
            {"indexed": True, "type": "address", "name": "to"},
            {"indexed": True, "type": "uint256", "name": "tokenId"}
        ],
        "name": "Transfer",
        "type": "event"
    },
    {
        "anonymous": False,
        "inputs": [
            {"indexed": True, "type": "address", "name": "owner"},
            {"indexed": True, "type": "address", "name": "approved"},
            {"indexed": True, "type": "uint256", "name": "tokenId"}
        ],
        "name": "Approval",
        "type": "event"
    },
    {
        "anonymous": False,
        "inputs": [
            {"indexed": True, "type": "address", "name": "owner"},
            {"indexed": True, "type": "address", "name": "operator"},
            {"indexed": False, "type": "bool", "name": "approved"}
        ],
        "name": "ApprovalForAll",
        "type": "event"
    }
]

# 合约实例化（替换为你的 NFT 合约地址）
NFT_ADDR = "0xCf7Ed3AccA5a467e9e704C703E8D87F634fB0Fc9"
nft_contract = w3.eth.contract(address=Web3.to_checksum_address(NFT_ADDR), abi=ERC721_ABI)
PRIVATE_KEY = "0xac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80"
deployer = w3.eth.account.from_key(PRIVATE_KEY)

if __name__ == "__main__":
    def get_nonce(address):
        return w3.eth.get_transaction_count(address)

    # 1. 读场景测试：查询 NFT 名称、符号、元数据
    print("=== 读方法测试 ===")
    print(f"NFT 名称: {nft_contract.functions.name().call()}")
    print(f"NFT 符号: {nft_contract.functions.symbol().call()}")
    print(w3.to_checksum_address(deployer.address))
    # 替换为已铸造的 tokenId 才能查询到 meta
    test_token_id = 1
    try:
        print(f"Token {test_token_id} 元数据: {nft_contract.functions.meta(test_token_id).call()}")
    except Exception as e:
        print(f"查询 Token {test_token_id} 元数据失败: {str(e)[:100]}")

    # 2. 写场景测试：owner 调用 safeMint 铸造 NFT
    print("\n=== 写方法测试 ===")
    TOKEN_ID = 1002
    meta_uri ="fufu_baidu.com"
    tx_mint = nft_contract.functions.safeMint(
        w3.to_checksum_address(deployer.address),
        TOKEN_ID,
        meta_uri
    ).build_transaction({
        "from": deployer.address,
        "nonce": get_nonce(deployer.address),
        "gas": 200000,
        "gasPrice": w3.eth.gas_price
    })
    signed_mint = w3.eth.account.sign_transaction(tx_mint, PRIVATE_KEY)

    try:
        tx_hash_mint = w3.eth.send_raw_transaction(signed_mint.raw_transaction)
    except Web3RPCError as e:
        print(e,type(e))
        print(parse_erc721_error(e))
