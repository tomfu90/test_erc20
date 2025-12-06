# test_eth_legacy_unit.py
# coding = utf-8
# author = fufu
# date = 12.03
import pytest
import allure
from eth_account import Account
from libs.utils import load_yaml
import json

# 加载测试用例
cases = load_yaml("yaml_case/unit/eth_legacy_unit.yaml")


@pytest.mark.parametrize("case", cases)
def test_eth_transfer_legacy_unit(case, web3):
    # 设置Allure标题和描述
    allure.dynamic.title(case["case_name"])
    allure.dynamic.description(case["description"])
    # 初始化账户和参数
    sender = Account.from_key(case["sender_pk"])
    recipient = web3.to_checksum_address(case["recipient"])
    amount_eth = case["input"]["amount"]
    gas = case["input"]["gas"]
    mark = case["mark"]
    #用公共夹具，维护nonce
    # 构造交易字典
    tx_dict = {
        "from": sender.address,
        "to": recipient,
        "value": web3.to_wei(amount_eth, "ether"),
        "gas": gas,  # 调高gas到25000
        "gasPrice": web3.eth.gas_price,
        "nonce": web3.eth.get_transaction_count(sender.address),
        "chainId": 31337,  # Hardhat/Ganache本地链ID
    }
    #allure转换
    tx_dict_str = json.dumps(tx_dict, indent=2, ensure_ascii=False)
    # 场景1：Gas不足（低于21000）
    if mark == "low":
        sign_tx = sender.sign_transaction(tx_dict)
        with allure.step("交易请求信息"):
            allure.attach(tx_dict_str, "交易体", attachment_type=allure.attachment_type.JSON)

        try:
            web3.eth.send_raw_transaction(sign_tx.raw_transaction)
        except Exception as e:
            err_msg = str(e).lower()
            with allure.step("交易-异常响应断言"):
                assert "requires at least 21000 gas" in err_msg, f"非预期异常：{err_msg}"

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
            allure.attach("篡改数据", "篡改信息", attachment_type=allure.attachment_type.TEXT)

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
            web3.eth.send_raw_transaction(sign_tx.raw_transaction)
        except Exception as e:
            err_msg = str(e).lower()
            with allure.step("交易-异常响应断言"):
                assert "doesn't have enough funds" in err_msg, f"非预期异常：{err_msg}"