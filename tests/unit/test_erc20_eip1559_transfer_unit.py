#test_erc20_eip1559_transfer_unit.py
# coding = utf-8
# author = fufu
# date = 12.03
import pytest
import allure
from eth_account import Account
from libs.utils import load_yaml
import json

# 加载测试用例
cases = load_yaml("yaml_case/unit/erc20_eip1559_transfer_unit.yaml")


@pytest.mark.parametrize("case", cases)
def test_erc20_transfer_eip1559_unit(case, web3,erc20_contract):
    # 设置Allure标题和描述
    allure.dynamic.title(case["case_name"])
    allure.dynamic.description(case["description"])
    # 读取yaml变量
    sender = Account.from_key(case["sender_pk"])
    recipient = web3.to_checksum_address(case["recipient"])
    amount_coin = case["input"]["amount"]
    gas = case["input"]["gas"]
    maxPriorityFeePerGas = case["input"]["maxPriorityFeePerGas"]
    maxFeePerGas = case["input"]["maxFeePerGas"]
    mark = case["mark"]
    #精度
    decimals =erc20_contract.functions.decimals().call()
    amount_coin = amount_coin * (10**decimals)
    # 构造交易字典
    tx_dict = {
        "from": sender.address,
        "to": erc20_contract.address,
        "value": web3.to_wei(0, "ether"),
        "gas": gas,
        "maxPriorityFeePerGas": web3.to_wei(maxPriorityFeePerGas, "gwei"),
        "maxFeePerGas": web3.to_wei(maxFeePerGas, "gwei"),
        "nonce": web3.eth.get_transaction_count(sender.address),
        "chainId": 31337,  # Hardhat/Ganache本地链ID
        "type": "0x2",
        "data": erc20_contract.functions.transfer(recipient, amount_coin).build_transaction({"from": sender.address,"gas": gas})["data"]
    }
    tx_dict_str = json.dumps(tx_dict, indent=2, ensure_ascii=False)
    # 场景1：Gas不足
    if mark == "low":
        sign_tx = sender.sign_transaction(tx_dict)
        with allure.step("交易请求信息"):
            allure.attach(tx_dict_str, "交易体", attachment_type=allure.attachment_type.JSON)

        try:
            web3.eth.send_raw_transaction(sign_tx.raw_transaction)
        except Exception as e:
            err_msg = str(e).lower()
            with allure.step("交易-异常响应断言"):
                assert "requires at least" in err_msg, f"非预期异常：{err_msg}"

    # 场景2：重复交易（Nonce过低，幂等校验）
    elif mark == "repeat":
        sign_tx = sender.sign_transaction(tx_dict)
        with allure.step("交易请求信息"):
            allure.attach(tx_dict_str, "交易体", attachment_type=allure.attachment_type.JSON)

        # 第一次发送交易（成功上链）
        tx_hash = web3.eth.send_raw_transaction(sign_tx.raw_transaction)
        receipt = web3.eth.wait_for_transaction_receipt(tx_hash)
        if receipt["status"] == 1:
            try:
                # 重复发送同一笔交易
                web3.eth.send_raw_transaction(sign_tx.raw_transaction)
            except Exception as e:
                err_msg = str(e).lower()
                with allure.step("交易-异常响应断言"):
                    assert "nonce too low" in err_msg, f"非预期异常：{err_msg}"


    # 场景3：签名篡改（确保gas足够，只触发验签失败）
    elif mark == "invalid_sign":
        # 1. 生成合法签名交易
        sign_tx = sender.sign_transaction(tx_dict)
        raw_tx = sign_tx.raw_transaction

        # 2. 篡改r字段为非法值（超过secp256k1曲线阶，直接触发验签失败）
        # secp256k1曲线阶：0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
        illegal_r = b"\xff" * 32  # 非法r值（超过曲线阶）
        modify_raw_tx = raw_tx[:-65] + illegal_r + raw_tx[-33:]  # 替换r字段（前32字节签名）

        with allure.step("交易请求信息"):
            allure.attach( "篡改数据", "篡改信息", attachment_type=allure.attachment_type.TEXT)

        try:
            web3.eth.send_raw_transaction(modify_raw_tx)
        except Exception as e:
            err_msg = str(e).lower()
            with allure.step("交易-异常响应断言"):
                # 匹配验签失败或gas异常（兜底）
                assert any(k in err_msg for k in ["invalid", "signature", "hash mismatch", "requires at least"]), \
                    f"非预期异常：{err_msg}"

    # 场景4：余额不足（转账金额超过账户余额）
    elif mark == "many":
        sign_tx = sender.sign_transaction(tx_dict)
        with allure.step("交易请求信息"):
            allure.attach(tx_dict_str, "交易体", attachment_type=allure.attachment_type.JSON)

        try:
            #发送交易
            tx_hash=web3.eth.send_raw_transaction(sign_tx.raw_transaction)
            #等待回执
            web3.eth.wait_for_transaction_receipt(tx_hash)
        except Exception as e:
            err_msg = str(e).lower()
            with allure.step("交易-异常响应断言"):
                # 匹配本地测试的自定义错误/通用revert关键词
                assert any(k in err_msg for k in ["reverted", "custom error", "balance"]), f"非预期异常：{err_msg}"

    # 场景5：maxFeePerGas设置错误
    elif mark == "fee_wrong":
        sign_tx = sender.sign_transaction(tx_dict)
        with allure.step("交易请求信息"):
            allure.attach(tx_dict_str, "交易体", attachment_type=allure.attachment_type.JSON)

        try:
            #发送交易
            web3.eth.send_raw_transaction(sign_tx.raw_transaction)
        except Exception as e:
            err_msg = str(e).lower()
            with allure.step("交易-异常响应断言"):
                assert "maxpriorityfeepergas" in str(e) or "bigger" in err_msg ,f"非预期异常{err_msg}"