# coding = utf-8
# author = fufu
# date = 12.03
import pytest
import allure
from eth_account import Account
from libs.utils import load_yaml
import json
cases =load_yaml("yaml_case/e2e/eth_legacy.yaml")

@pytest.mark.parametrize("case", cases["success"])
def test_eth_transfer_legacy_sucess(case,web3):
    #设置allure标题
    allure.dynamic.title(case["case_name"])
    allure.dynamic.description(case["description"])
    #Account.from_key(私钥)推导账户对象用来签名
    sender =Account.from_key(case["sender_pk"])
    #接受地址，用web3.to_checksum_address 确包地址符合eip-55标准
    recipient =web3.to_checksum_address(case["recipient"])
    #转账金额
    amount_eth=case["amount"]
    #转账前-转账地址eth数量;接受地址eth数量
    before_sender = web3.eth.get_balance(sender.address)
    before_recipient = web3.eth.get_balance(recipient)
    # 构造交易体
    tx_dict ={
        "from": sender.address,
        "to": recipient,
        "value": web3.to_wei(amount_eth, "ether"),
        "gas": 21000, #eth固定21000
        "gasPrice": web3.eth.gas_price,
        "nonce": web3.eth.get_transaction_count(sender.address),
        "chainId": 31337, #hardhad节点
    }
    tx_dict_str = json.dumps(tx_dict, indent=2, ensure_ascii=False)
    # 本地签名
    sign_tx = sender.sign_transaction(tx_dict)
    # 发送交易
    tx_hash = web3.eth.send_raw_transaction(sign_tx.raw_transaction)
    # allure封装交易信息信息
    with allure.step("交易请求信息"):
        allure.attach(tx_dict_str,"交易体",attachment_type=allure.attachment_type.JSON)
    # 等待链上响应
    receipt = web3.eth.wait_for_transaction_receipt(tx_hash)
    with allure.step("交易结果信息"):
        allure.attach(f"交易哈希：{tx_hash.hex()}\n区块号：{receipt['blockNumber']}", "交易关键信息",allure.attachment_type.TEXT)
    assert receipt["status"] == 1, "交易失败"
    assert receipt["from"].lower() == sender.address.lower()
    assert receipt["to"].lower() == recipient.lower()
    # 转账数量校验,要从web3.eth.get_transaction这里获取
    tx = web3.eth.get_transaction(tx_hash)
    amount_block = web3.from_wei(tx["value"], "ether")
    assert  float(amount_block)== amount_eth,f"发起转账金额{amount_eth} != 链上金额{amount_block}"
    # 转账成功后 接受地址数量校验,全部用wei计算，amount_eth单位是eth要转换成wei
    with allure.step("接收方余额校验"):
        after_receipt = web3.eth.get_balance(recipient)
        amount_eth_wei = web3.to_wei(amount_eth, "ether")
        assert before_recipient + amount_eth_wei == after_receipt,f"接受地址｜转账后链上余额：{after_receipt} ！= 转账前{before_recipient} +转账{amount_eth_wei}"
    # 转账成功后，转账地址数量校验公式：转账前数量-手续费-转账数量=转账后数量
    with allure.step("计算手续费，转账地址余额校验"):
        after_sender = web3.eth.get_balance(sender.address)
        # 手续费
        gas_used =receipt["gasUsed"]
        gas_price = receipt["effectiveGasPrice"]
        fee = gas_used * gas_price
        assert before_sender-fee-amount_eth_wei == after_sender,f"转账地址｜转账前余额：{before_sender} - 手续费{fee} -转账{amount_eth_wei} != 转账后{after_sender}"












