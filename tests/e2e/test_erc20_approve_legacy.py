# test_erc20_approve_legacy.py
# coding = utf-8
# author = fufu
# date = 12.03
import pytest
import allure
from eth_account import Account
from libs.utils import load_yaml
import json
cases =load_yaml("yaml_case/e2e/erc20_approve_legacy.yaml")

@pytest.mark.parametrize("case", cases["success"])
def test_erc20_approve_legacy_success(case,web3,erc20_contract):
    #设置allure标题
    allure.dynamic.title(case["case_name"])
    allure.dynamic.description(case["description"])
    #Account.from_key(私钥)推导账户对象用来签名
    owner =Account.from_key(case["sender_pk"])      #授权方（代币所有者）
    #接受地址，用web3.to_checksum_address 确包地址符合eip-55标准
    spender =web3.to_checksum_address(case["recipient"]) #被授权方
    #授权金额
    amount_usdt=case["approve_amount"]
    #精度
    decimals=erc20_contract.functions.decimals().call()
    amount_approve =int(amount_usdt * (10**decimals))
    # 构造交易体
    tx_dict ={
        "from": owner.address,
        "to": erc20_contract.address, # 目标：ERC20合约地址（不是接收方）
        "value": web3.to_wei(0, "ether"), # ETH金额为0，代币金额在data里
        "gas": 60000, # Legacy approve固定Gas足够
        "gasPrice": web3.eth.gas_price, # Legacy核心参数：gasPrice
        "nonce": web3.eth.get_transaction_count(owner.address),
        "chainId": 31337, #hardhad节点
        # 关键：编码transfer方法调用（to地址 + 代币最小单位金额）
        "data": erc20_contract.functions.approve(spender, amount_approve).build_transaction({"from": owner.address})["data"]
    }
    tx_dict_str = json.dumps(tx_dict, indent=2, ensure_ascii=False)
    # 本地签名
    sign_tx = owner.sign_transaction(tx_dict)
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
    assert receipt["from"].lower() == owner.address.lower()
    assert receipt["to"].lower() == erc20_contract.address.lower()
    # 解析approve事件校验
    with allure.step("解析Approval事件校验"):
        approve_event = erc20_contract.events.Approval().process_log(receipt["logs"][0])
        assert approve_event["args"]["owner"].lower() == owner.address.lower()
        assert approve_event["args"]["spender"].lower() == spender.lower()
        assert approve_event["args"]["value"] == amount_approve ,f"日志事件转账金额{approve_event["value"]} ！=发起交易的金额{amount_approve}"
    # 用allowance接口校验
    with allure.step("链上授权额度检查"):
        actual_amount = erc20_contract.functions.allowance(owner.address,spender).call()
        assert actual_amount == amount_approve ,f"连上授权额度{actual_amount} != 授权请求金额{amount_approve}"












