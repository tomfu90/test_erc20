# conftest.py
# coding = utf-8
# author = fufu
import pytest
from eth_account import Account
from web3 import Web3
import sys,os
import time
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0,project_root)
#夹具1 初始化本地节点（全局唯一，确保连接成功）
@pytest.fixture(scope="session")
def web3():
    w3=Web3(Web3.HTTPProvider("http://127.0.0.1:8545"))
    assert w3.is_connected()," ☹️本地节点未启动！请先启动节点再运行测试"
    print("😊本地节点初始化成功")
    yield w3

# 夹具2：初始化ERC20合约（全局复用，传入固定合约地址/ABI）
@pytest.fixture(scope="session")
def erc20_contract(web3):
    # 固定合约ABI（仅保留核心功能，精简）
    token_abi = [
        {"inputs": [], "name": "decimals", "outputs": [{"internalType": "uint8", "name": "", "type": "uint8"}], "type": "function"},
        {"inputs": [{"internalType": "address", "name": "to", "type": "address"}, {"internalType": "uint256", "name": "amount", "type": "uint256"}], "name": "transfer", "outputs": [{"internalType": "bool", "name": "", "type": "bool"}], "type": "function"},
        {"inputs": [{"internalType": "address", "name": "spender", "type": "address"}, {"internalType": "uint256", "name": "amount", "type": "uint256"}], "name": "approve", "outputs": [{"internalType": "bool", "name": "", "type": "bool"}], "type": "function"},
        {"inputs": [{"internalType": "address", "name": "from", "type": "address"}, {"internalType": "address", "name": "to", "type": "address"}, {"internalType": "uint256", "name": "amount", "type": "uint256"}], "name": "transferFrom", "outputs": [{"internalType": "bool", "name": "", "type": "bool"}], "type": "function"},
        {"inputs": [{"internalType": "address", "name": "account", "type": "address"}], "name": "balanceOf", "outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}], "type": "function"},
        {"inputs": [{"internalType": "address", "name": "owner", "type": "address"}, {"internalType": "address", "name": "spender", "type": "address"}], "name": "allowance", "outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}], "type": "function"},
        {"anonymous": False, "inputs": [{"indexed": True, "internalType": "address", "name": "from", "type": "address"}, {"indexed": True, "internalType": "address", "name": "to", "type": "address"}, {"indexed": False, "internalType": "uint256", "name": "value", "type": "uint256"}], "name": "Transfer", "type": "event"},
        {"anonymous": False, "inputs": [{"indexed": True, "internalType": "address", "name": "owner", "type": "address"}, {"indexed": True, "internalType": "address", "name": "spender", "type": "address"}, {"indexed": False, "internalType": "uint256", "name": "value", "type": "uint256"}], "name": "Approval", "type": "event"}
    ]
    # 本地节点部署的地址
    token_addr = "0x5FbDB2315678afecb367f032d93F642f64180aa3"
    contract = web3.eth.contract(address=token_addr, abi=token_abi)
    print("😊 ERC20合约初始化成功")
    yield contract

