# test_erc20_transfer_legacy.py
# coding = utf-8
# author = fufu
# date = 12.03
import pytest
import allure
from eth_account import Account
from libs.utils import load_yaml
import json
cases =load_yaml("yaml_case/e2e/erc20_transfer_legacy.yaml")

@pytest.mark.parametrize("case", cases["success"])
def test_erc20_transfer_legacy_success(case,web3,erc20_contract):
    #设置allure标题
    allure.dynamic.title(case["case_name"])
    allure.dynamic.description(case["description"])
    #Account.from_key(私钥)推导账户对象用来签名
    sender =Account.from_key(case["sender_pk"])
    #接受地址，用web3.to_checksum_address 确包地址符合eip-55标准
    recipient =web3.to_checksum_address(case["recipient"])
    #转账金额
    amount_usdt=case["amount"]
    #精度
    decimals=erc20_contract.functions.decimals().call()
    amount_transfer =int(amount_usdt * (10**decimals))
    #转账前-转账地址usdt数量;接受地址usdt数量
    before_sender =erc20_contract.functions.balanceOf(sender.address).call()
    before_recipient =erc20_contract.functions.balanceOf(recipient).call()

    # 构造交易体
    tx_dict ={
        "from": sender.address,
        "to": erc20_contract.address, # 目标：ERC20合约地址（不是接收方）
        "value": web3.to_wei(0, "ether"), # ETH金额为0，代币金额在data里
        "gas": 60000, # ERC20转账gas比ETH高（建议设60000，足够大部分合约）
        "gasPrice": web3.eth.gas_price,
        "nonce": web3.eth.get_transaction_count(sender.address),
        "chainId": 31337, #hardhad节点
        # 关键：编码transfer方法调用（to地址 + 代币最小单位金额）
        "data": erc20_contract.functions.transfer(recipient, amount_transfer).build_transaction({"from": sender.address})["data"]
    }
    tx_dict_str = json.dumps(tx_dict, indent=2, ensure_ascii=False)
    # 本地签名
    sign_tx = sender.sign_transaction(tx_dict)
    # 发送交易
    tx_hash = web3.eth.send_raw_transaction(sign_tx.raw_transaction)
    # allure封装交易信息信息
    with allure.step("交易请求信息"):
        allure.attach(tx_dict_str,"交易体",attachment_type=allure.attachment_type.JSON)
    # 等待链上响应回执并校验
    receipt = web3.eth.wait_for_transaction_receipt(tx_hash)
    with allure.step("交易结果信息"):
        allure.attach(f"交易哈希：{tx_hash.hex()}\n区块号：{receipt['blockNumber']}", "交易关键信息",allure.attachment_type.TEXT)
    #基础校验
    assert receipt["status"] == 1, "交易失败"
    assert receipt["from"].lower() == sender.address.lower()
    assert receipt["to"].lower() == erc20_contract.address.lower()
    # 转账数量校验,解析tansfer日志事件
    with allure.step("解析Transfer事件校验"):
        transfer_event = erc20_contract.events.Transfer().process_log(receipt["logs"][0])
        assert transfer_event["args"]["from"].lower() == sender.address.lower()
        assert transfer_event["args"]["to"].lower() == recipient.lower()
        assert transfer_event["args"]["value"] == amount_transfer ,f"日志事件转账金额{transfer_event["value"]} ！=发起交易的金额{amount_transfer}"
    # 转账成功后 接受地址数量校验,全部用wei计算，amount_eth单位是eth要转换成wei
    with allure.step("接收方余额校验"):
        after_receipt = erc20_contract.functions.balanceOf(recipient).call()
        assert before_recipient + amount_transfer == after_receipt,f"接受地址｜转账后链上余额：{after_receipt} ！= 转账前{before_recipient} +转账{amount_transfer}"
    # 转账成功后，转账地址数量校验公式：转账前数量-手续费-转账数量=转账后数量
    with allure.step("转账地址余额校验"):
        after_sender = erc20_contract.functions.balanceOf(sender.address).call()
        assert before_sender-amount_transfer == after_sender,f"转账地址｜转账前余额：{before_sender}  -转账{amount_transfer} != 转账后{after_sender}"












