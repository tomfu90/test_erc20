# demo.py
# fufu
from local_node_utils import *
from eth_account import Account
print("节点是否连接：", w3.is_connected())  # 无参数！
accounts = w3.eth.accounts
#1 ☑️查询代币 名称/精度/符号
# 合约代币精度
decimals = token.functions.decimals().call()  # 通常是 18
# 合约名字
name = token.functions.name().call()
# 合约符号
symbol = token.functions.symbol().call()
#2 ☑️校验地址余额是否正确，1 存在地址是否合规 2 地址是否有余额
address_invalid = "123"  #地址不合规：False ; web3.exceptions.InvalidAddress: ENS name: '123' is invalid.
address_valid = "0x49738b8b9cbfb4fa1f7eb1e76e151226f26cf0b9"  #地址合规：True
address_success = accounts[0] #地址合规：True
# 3符合 EIP-55 标准的 Checksum 地址 ： #不符合规则 抛异常
# 4查询eth余额
address_new =w3.to_checksum_address(address_valid)
print(address_new )
balance_valid=w3.eth.get_balance(address_new)
balance_success=w3.eth.get_balance(address_success)
#得出来的是wei,需要转换为eth
balance1 = w3.from_wei(balance_valid, "ether")
balance2 = w3.from_wei(balance_success, "ether")
print(f"eth余额：有效地址但不是系统内部生成的{balance1}；系统内部地址{balance2}")
# 5查询代币余额，调用合约方法token.functions.balanceOf
#地址非法；不符合规则，抛异常
balance_u1 = token.functions.balanceOf(address_new).call() / (10 ** decimals)
balance_u2 = token.functions.balanceOf(address_success).call() /  (10 ** decimals)
print(f"{symbol}代币余额：有效地址但不是系统内部生成的{balance_u1}；系统内部地址{balance_u2}")
address_new =w3.to_checksum_address(accounts[0])
balance_u2 = token.functions.balanceOf(address_new).call()/  (10 ** decimals)
print(f"最新余额{balance_u2}")
Private_Key ="0xac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80"
sender= Account.from_key(Private_Key)
recipient = w3.to_checksum_address(accounts[-1])
# eth -legacy

#erc20- eip-1559

# transfer_amount = 1000 * (10 ** decimals)
# tx_dict = token.functions.transfer(recipient, transfer_amount).build_transaction({
#     "from": sender.address,
#     "maxPriorityFeePerGas":w3.to_wei(2, "gwei"),
#     "maxFeePerGas":w3.to_wei(10, "gwei"),
#     "nonce": w3.eth.get_transaction_count(sender.address),
#     'chainId': 31337
# })
# # 2️⃣ 估算 gas（可选，build_transaction 有时会自动填 gas，但显式更安全）
# tx_dict["gas"] = int(w3.eth.estimate_gas(tx_dict) * 1.2)
# # 3️⃣ ✅ 本地签名（传入 tx_dict）
# signed_tx = sender.sign_transaction(tx_dict)
# # 4️⃣ ✅ 发送 raw transaction
# tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
# print(f"📤 转账交易已发送: {tx_hash.hex()}")
# # 5️⃣ 等待确认（可选）
# receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
# if receipt.status == 1:
#     print(f"usdt -eip1559 转账成功")
#     print("blockNumber:",receipt["blockNumber"])
#     print("gasUsed:", receipt["gasUsed"])
#     print("hash:", receipt["transactionHash"])
#     print("hash_hex:", receipt["transactionHash"].hex())
#     print("from:", receipt["from"])
#     print("to:", receipt["to"])
#     print("effectiveGasPrice:",w3.from_wei(receipt.effectiveGasPrice, "gwei"))
#     fee_decimals = receipt["gasUsed"] * receipt.effectiveGasPrice
#     fee_eth =w3.from_wei(fee_decimals, "ether")
#     print("fee_eth", fee_eth)
#     #通过区块详情拿到base_fee
#     block = w3.eth.get_block(receipt["blockNumber"])
#     print("block:", block)
#     base_fee = block["baseFeePerGas"]
#     print("base_fee:", w3.from_wei(base_fee, "gwei"))
#     maxPriorityFeePerGas =receipt.effectiveGasPrice - base_fee
#     print("maxPriorityFeePerGas:", w3.from_wei(maxPriorityFeePerGas, "gwei"))
#     transfer_event_parser = token.events.Transfer()
#     for log in receipt.logs:
#         decoded_log = transfer_event_parser.process_log(log)
#         amount_deciamls = decoded_log["args"]["value"]
#         amount_usdt = amount_deciamls / (10**decimals)
#         print("amount_usdt:", amount_usdt)
# else:
#     print("转账失败")
# erc20 -Legacy
# tx_dict = token.functions.transfer(recipient, transfer_amount).build_transaction({
#     "from": sender.address,
#     "gasPrice": w3.to_wei(10, "gwei"),
#     "nonce": w3.eth.get_transaction_count(sender.address),
#     'chainId': 31337
# })
# tx_dict["gas"] = int(w3.eth.estimate_gas(tx_dict) * 1.2)
# signed_tx = sender.sign_transaction(tx_dict)
# tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
# receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
# if receipt.status == 1:
#     print(f"usdt legacy转账成功")
#     print("blockNumber:",receipt["blockNumber"])
#     print("gasUsed:", receipt["gasUsed"])
#     print("hash:", receipt["transactionHash"])
#     print("hash_hex:", receipt["transactionHash"].hex())
#     print("from:", receipt["from"])
#     print("to:", receipt["to"])
#     # 1. 修正：生成Transfer事件解析器（关键！）
#     transfer_event_parser = token.events.Transfer()
#     for log in receipt.logs:
#         #日志事件查询转账金额
#         decoded_log = transfer_event_parser.process_log(log)
#         print(decoded_log)
#         amount_decimals = decoded_log["args"]["value"]
#         amount_eth = amount_decimals / (10**decimals)
#         print("amount_eth",amount_eth)
#         fee = receipt["gasUsed"] * w3.from_wei(10, "gwei")
#         print("fee_eth",fee)


# 授权成功 -eip-1559
# 查询授权额度
# 授权转账成功


