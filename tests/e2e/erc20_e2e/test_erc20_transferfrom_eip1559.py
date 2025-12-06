# test_erc20_transferfrom_eip1559.py
# coding = utf-8
# author = fufu
# date = 12.03
import pytest
import allure
from eth_account import Account
import json
from libs.utils import load_yaml
cases =load_yaml("yaml_case/e2e/erc20_transferfrom_eip1559.yaml")

@pytest.mark.parametrize("case", cases["success"])
def test_erc20_approve_legacy_success(case,web3,erc20_contract):
    #设置allure标题
    allure.dynamic.title(case["case_name"])
    allure.dynamic.description(case["description"])
    #Account.from_key(私钥)推导账户对象用来签名
    owner =Account.from_key(case["owner_pk"])      #授权方（代币所有者）
    #被授权地址，用web3.to_checksum_address 确包地址符合eip-55标准
    spender =web3.to_checksum_address(case["spender"]) #被授权方
    spender_obj = Account.from_key(case["spender_pk"])
    #授权转账的第三方接受地址
    recipient_address =web3.to_checksum_address(case["receipt"]) #第三方接受地址
    #授权金额
    amount_approve=case["approve_amount"]
    #授权转账金额
    transfer_amount=case["transfer_amount"]
    #精度
    decimals=erc20_contract.functions.decimals().call()
    amount_approve =int(amount_approve * (10**decimals))
    transfer_amount=int(transfer_amount *( 10**decimals))
    # 预估gas量-approve
    approve_temp_tx ={
        "from": owner.address,
        "to": erc20_contract.address,
        "value": web3.to_wei(0, "ether"),
        "data": erc20_contract.functions.approve(spender,amount_approve).build_transaction({"from":owner.address})["data"],
        "maxPriorityFeePerGas": web3.to_wei(2, "gwei"),
        "maxFeePerGas": web3.to_wei(20, "gwei"),
        "chainId": 31337

    }
    approve_gas_limit = web3.eth.estimate_gas(approve_temp_tx) +500
    # 构造授权交易体
    approve_tx_dict ={
        "from": owner.address,
        "to": erc20_contract.address, # 目标：ERC20合约地址（不是接收方）
        "value": web3.to_wei(0, "ether"), # ETH金额为0，代币金额在data里
        "gas": approve_gas_limit,
        "maxPriorityFeePerGas": web3.to_wei(2, "gwei"),
        "maxFeePerGas": web3.to_wei(20, "gwei"),
        "nonce": web3.eth.get_transaction_count(owner.address),
        "chainId": 31337, #hardhad节点
        "type": "0x2",  # 标记为 EIP1559 交易
        "data": erc20_contract.functions.approve(spender, amount_approve).build_transaction({"from": owner.address})["data"]
    }
    tx_dict_str = json.dumps(approve_tx_dict, indent=2, ensure_ascii=False)
    # 本地签名
    sign_tx = owner.sign_transaction(approve_tx_dict)
    # 发送交易
    tx_hash = web3.eth.send_raw_transaction(sign_tx.raw_transaction)
    # allure封装交易信息信息
    with allure.step("授权交易请求信息"):
        allure.attach(tx_dict_str,"交易体",attachment_type=allure.attachment_type.JSON)
    # 等待链上响应回执并校验
    receipt = web3.eth.wait_for_transaction_receipt(tx_hash)
    with allure.step("授权交易结果信息"):
        # 容错处理：避免 None 调用方法/属性
        tx_hash_str = tx_hash.hex() if tx_hash else "交易哈希获取失败"
        block_num = receipt.get("blockNumber", "区块号获取失败") if receipt else "交易回执为空"
        allure.attach(f"交易哈希：{tx_hash_str}\n区块号：{block_num}", "交易关键信息",allure.attachment_type.TEXT)
    if receipt["status"] == 1:
        # 授权转账前，代币持有者数量；第三方接受地址余额
        before_owner_amount = erc20_contract.functions.balanceOf(owner.address).call()
        before_receipt_amount = erc20_contract.functions.balanceOf(recipient_address).call()
        # 授权转账前授权额度查询
        before_allowance_amount =erc20_contract.functions.allowance(owner.address,spender).call()
        with (allure.step("授权交易链上查询额度")):
            actual_amount = erc20_contract.functions.allowance(owner.address, spender).call()
            assert actual_amount == amount_approve,f"链上额度{actual_amount/(10**decimals)} 交易发起额度{amount_approve/(10**decimals)}"
        #有授权额度，才进行授权转账
            # 预估gas量-transferFrom
            transferFrom_temp_tx = {
                "from": spender,
                "to": erc20_contract.address,
                "value": web3.to_wei(0, "ether"),
                "data": erc20_contract.functions.transferFrom(owner.address, recipient_address,transfer_amount).build_transaction(
                    {"from": spender})["data"],
                "maxPriorityFeePerGas": web3.to_wei(2, "gwei"),
                "maxFeePerGas": web3.to_wei(20, "gwei"),
                "chainId": 31337

            }
            transferFrom_gas_limit = web3.eth.estimate_gas(transferFrom_temp_tx) + 5000
            # 构造授权转账交易体
            transfer_from_tx_dict = {
                "from": spender, #被授权方
                "to": erc20_contract.address,  # 目标：ERC20合约地址（不是接收方）
                "value": web3.to_wei(0, "ether"),  # ETH金额为0，代币金额在data里
                "gas": transferFrom_gas_limit,
                "maxPriorityFeePerGas": web3.to_wei(2, "gwei"),
                "maxFeePerGas": web3.to_wei(20, "gwei"),
                "nonce": web3.eth.get_transaction_count(spender),
                "chainId": 31337,  # hardhad节点
                # 关键：编码transfer方法调用（to地址 + 代币最小单位金额）
                "data": erc20_contract.functions.transferFrom(owner.address,recipient_address, transfer_amount).build_transaction(
                    {"from": spender})["data"],
                "type": "0x2"
            }
            tx_dict_str = json.dumps(transfer_from_tx_dict, indent=2, ensure_ascii=False)
            with allure.step("授权转账交易请求信息"):
                allure.attach(tx_dict_str, "交易体", attachment_type=allure.attachment_type.JSON)
            # 本地签名
            transfer_from_sign_tx = spender_obj.sign_transaction(transfer_from_tx_dict)
            # 发送交易
            transfer_from_tx_hash = web3.eth.send_raw_transaction(transfer_from_sign_tx.raw_transaction)
            # 等待交易回执
            transfer_from_receipt = web3.eth.wait_for_transaction_receipt(transfer_from_tx_hash)
            with allure.step("授权转账交易结果信息"):
                allure.attach(f"交易哈希：{transfer_from_tx_hash.hex()}\n区块号：{transfer_from_receipt['blockNumber']}", "交易关键信息",allure.attachment_type.TEXT)
            #基础信息校验
            assert transfer_from_receipt["status"] ==1 ,f"交易失败"
            assert transfer_from_receipt["from"].lower() == spender.lower()
            assert transfer_from_receipt["to"].lower() == erc20_contract.address.lower()
            # 授权转账后，代币持有者数量；第三方接受地址余额
            after_owner_amount = erc20_contract.functions.balanceOf(owner.address).call()
            after_receipt_amount = erc20_contract.functions.balanceOf(recipient_address).call()
            # 授权转账后授权额度查询
            after_allowance_amount = erc20_contract.functions.allowance(owner.address, spender).call()
            #从日志事件获取转账金额
            transfer_event = erc20_contract.events.Transfer().process_log(transfer_from_receipt["logs"][0])
            transfer_value = transfer_event["args"]["value"]
            with allure.step("授权转账-第三方接受地址余额校验"):
                assert before_receipt_amount + transfer_value == after_receipt_amount \
                ,f"第三方接受地址：起始金额{before_receipt_amount/(10**decimals)}+账变金额{transfer_value/(10**decimals)} ！= 期末余额{after_receipt_amount/(10**decimals)}"
            with allure.step("授权转账-授权地址（代币持有）余额校验"):
                assert before_owner_amount - transfer_value == after_owner_amount \
                ,f"授权地址：起始金额{before_owner_amount / (10 ** decimals)}-账变金额{transfer_value / (10 ** decimals)} != 期末余额{after_owner_amount / (10 ** decimals)}"
            with allure.step("授权转账-授权额度校验"):
                assert before_allowance_amount - transfer_value == after_allowance_amount \
                ,f"授权额度：起始授权金额{before_allowance_amount / (10 ** decimals)}-账变金额{transfer_value / (10 ** decimals)} != 期末余额{after_allowance_amount / (10 ** decimals)}"
















