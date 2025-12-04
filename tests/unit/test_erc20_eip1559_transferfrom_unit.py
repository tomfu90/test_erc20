#test_erc20_eip1559_transferfrom_unit.py
# coding = utf-8
# author = fufu
# date = 12.03
import pytest
import allure
from eth_account import Account
from libs.utils import load_yaml
import json

# 加载测试用例
cases = load_yaml("yaml_case/unit/erc20_eip1559_transferfrom_unit.yaml")


@pytest.mark.parametrize("case", cases)
def test_erc20_transferfrom_eip1559_unit(case, web3,erc20_contract):
    # 设置Allure标题和描述
    allure.dynamic.title(case["case_name"])
    allure.dynamic.description(case["description"])
    # 读取yaml变量
    owner = Account.from_key(case["owner_pk"])  # 授权方（代币所有者）
    # 被授权地址，用web3.to_checksum_address 确包地址符合eip-55标准
    spender = web3.to_checksum_address(case["spender"])  # 被授权方
    spender_obj = Account.from_key(case["spender_pk"])
    # 授权转账的第三方接受地址
    recipient_address = web3.to_checksum_address(case["receipt"])  # 第三方接受地址
    # 授权金额
    amount_approve = case["input"]["approve_amount"]
    # 授权转账金额
    transfer_amount = case["input"]["transfer_amount"]
    # 精度
    decimals = erc20_contract.functions.decimals().call()
    amount_approve = int(amount_approve * (10 ** decimals))
    transfer_amount = int(transfer_amount * (10 ** decimals))
    gas = case["input"]["gas"]
    maxPriorityFeePerGas = case["input"]["maxPriorityFeePerGas"]
    maxFeePerGas = case["input"]["maxFeePerGas"]
    mark = case["mark"]
    # # 获取当前区块 base fee
    # latest_block = web3.eth.get_block('latest')
    # base_fee = latest_block['baseFeePerGas']
    # safe_max_priority_fee = web3.to_wei(2, 'gwei')
    # safe_max_fee = base_fee + safe_max_priority_fee

    if mark =="low_gas":
        # 预估gas量-approve
        approve_temp_tx = {
            "from": owner.address,
            "to": erc20_contract.address,
            "value": web3.to_wei(0, "ether"),
            "data":
                erc20_contract.functions.approve(spender, amount_approve).build_transaction({"from": owner.address})[
                    "data"],
            "maxPriorityFeePerGas": web3.to_wei(2, "gwei"),
            "maxFeePerGas": web3.to_wei(40, "gwei"),
            "chainId": 31337

        }
        approve_gas_limit = web3.eth.estimate_gas(approve_temp_tx) + 500
        # 构造授权交易体
        approve_tx_dict = {
            "from": owner.address,
            "to": erc20_contract.address,  # 目标：ERC20合约地址（不是接收方）
            "value": web3.to_wei(0, "ether"),  # ETH金额为0，代币金额在data里
            "gas": approve_gas_limit,
            "maxPriorityFeePerGas": web3.to_wei(2, "gwei"),
            "maxFeePerGas": web3.to_wei(40, "gwei"),
            "nonce": web3.eth.get_transaction_count(owner.address),
            "chainId": 31337,  # hardhad节点
            "type": "0x2",  # 标记为 EIP1559 交易
            "data":
                erc20_contract.functions.approve(spender, amount_approve).build_transaction({"from": owner.address})[
                    "data"]
        }
        # 本地签名
        sign_tx = owner.sign_transaction(approve_tx_dict)
        # 发送交易
        tx_hash = web3.eth.send_raw_transaction(sign_tx.raw_transaction)
        # 等待链上响应回执并校验
        receipt = web3.eth.wait_for_transaction_receipt(tx_hash)
        assert receipt["status"] == 1,"授权失败"
        # 构造授权转账交易体
        transfer_from_tx_dict = {
            "from": spender,  # 被授权方
            "to": erc20_contract.address,  # 目标：ERC20合约地址（不是接收方）
            "value": web3.to_wei(0, "ether"),  # ETH金额为0，代币金额在data里
            "gas": gas,
            "maxPriorityFeePerGas": web3.to_wei(maxPriorityFeePerGas, "gwei"),
            "maxFeePerGas": web3.to_wei(maxFeePerGas, "gwei"),
            "nonce": web3.eth.get_transaction_count(spender),
            "chainId": 31337,  # hardhad节点
            # 关键：编码transfer方法调用（to地址 + 代币最小单位金额）
            "data": erc20_contract.functions.transferFrom(owner.address, recipient_address,
                                                          transfer_amount).build_transaction(
                {"from": spender,"gas":gas})["data"],
            "type": "0x2"
        }
        tx_dict_str = json.dumps(transfer_from_tx_dict, indent=2, ensure_ascii=False)
        with allure.step("授权转账交易请求信息"):
            allure.attach(tx_dict_str, "交易体", attachment_type=allure.attachment_type.JSON)
        # 本地签名
        transfer_from_sign_tx = spender_obj.sign_transaction(transfer_from_tx_dict)
        # 发送交易，捕获一场，断言
        try:
            web3.eth.send_raw_transaction(transfer_from_sign_tx.raw_transaction)
        except Exception as e:
            err_msg = str(e).lower()
            with allure.step("交易-异常响应断言"):
                assert "requires at least" in err_msg, f"非预期异常：{err_msg}"

    elif mark == "low_coin":
        # 预估gas量-approve
        approve_temp_tx = {
            "from": owner.address,
            "to": erc20_contract.address,
            "value": web3.to_wei(0, "ether"),
            "data":
                erc20_contract.functions.approve(spender, amount_approve).build_transaction({"from": owner.address})[
                    "data"],
            "maxPriorityFeePerGas": web3.to_wei(2, "gwei"),
            "maxFeePerGas": web3.to_wei(40, "gwei"),
            "chainId": 31337

        }
        approve_gas_limit = web3.eth.estimate_gas(approve_temp_tx) + 500
        # 构造授权交易体
        approve_tx_dict = {
            "from": owner.address,
            "to": erc20_contract.address,  # 目标：ERC20合约地址（不是接收方）
            "value": web3.to_wei(0, "ether"),  # ETH金额为0，代币金额在data里
            "gas": approve_gas_limit,
            "maxPriorityFeePerGas": web3.to_wei(2, "gwei"),
            "maxFeePerGas": web3.to_wei(40, "gwei"),
            "nonce": web3.eth.get_transaction_count(owner.address),
            "chainId": 31337,  # hardhad节点
            "type": "0x2",  # 标记为 EIP1559 交易
            "data":
                erc20_contract.functions.approve(spender, amount_approve).build_transaction({"from": owner.address})[
                    "data"]
        }
        # 本地签名
        sign_tx = owner.sign_transaction(approve_tx_dict)
        # 发送交易
        tx_hash = web3.eth.send_raw_transaction(sign_tx.raw_transaction)
        # 等待链上响应回执并校验
        receipt = web3.eth.wait_for_transaction_receipt(tx_hash)
        assert receipt["status"] == 1, "授权失败"
        # 构造授权转账交易体
        transfer_from_tx_dict = {
            "from": spender,  # 被授权方
            "to": erc20_contract.address,  # 目标：ERC20合约地址（不是接收方）
            "value": web3.to_wei(0, "ether"),  # ETH金额为0，代币金额在data里
            "gas": gas,
            "maxPriorityFeePerGas": web3.to_wei(maxPriorityFeePerGas, "gwei"),
            "maxFeePerGas": web3.to_wei(maxFeePerGas, "gwei"),
            "nonce": web3.eth.get_transaction_count(spender),
            "chainId": 31337,  # hardhad节点
            # 关键：编码transfer方法调用（to地址 + 代币最小单位金额）
            "data": erc20_contract.functions.transferFrom(owner.address, recipient_address,
                                                          transfer_amount).build_transaction(
                {"from": spender, "gas": gas})["data"],
            "type": "0x2"
        }
        tx_dict_str = json.dumps(transfer_from_tx_dict, indent=2, ensure_ascii=False)
        with allure.step("授权转账交易请求信息"):
            allure.attach(tx_dict_str, "交易体", attachment_type=allure.attachment_type.JSON)
        # 本地签名
        transfer_from_sign_tx = spender_obj.sign_transaction(transfer_from_tx_dict)
        # 发送交易
        try:
            web3.eth.send_raw_transaction(transfer_from_sign_tx.raw_transaction)
        except Exception as e:
            err_msg = str(e).lower()
            with allure.step("交易-断言"):
                # 匹配 ERC20 余额不足
                assert "reverted" in err_msg
    elif mark == "cancel":
        # 预估gas量-approve
        approve_temp_tx = {
            "from": owner.address,
            "to": erc20_contract.address,
            "value": web3.to_wei(0, "ether"),
            "data":
                erc20_contract.functions.approve(spender, amount_approve).build_transaction({"from": owner.address})[
                    "data"],
            "maxPriorityFeePerGas": web3.to_wei(2, "gwei"),
            "maxFeePerGas": web3.to_wei(40, "gwei"),
            "chainId": 31337

        }
        approve_gas_limit = web3.eth.estimate_gas(approve_temp_tx) + 500
        # 构造授权交易体
        approve_tx_dict = {
            "from": owner.address,
            "to": erc20_contract.address,  # 目标：ERC20合约地址（不是接收方）
            "value": web3.to_wei(0, "ether"),  # ETH金额为0，代币金额在data里
            "gas": approve_gas_limit,
            "maxPriorityFeePerGas": web3.to_wei(2, "gwei"),
            "maxFeePerGas": web3.to_wei(40, "gwei"),
            "nonce": web3.eth.get_transaction_count(owner.address),
            "chainId": 31337,  # hardhad节点
            "type": "0x2",  # 标记为 EIP1559 交易
            "data":
                erc20_contract.functions.approve(spender, amount_approve).build_transaction({"from": owner.address})[
                    "data"]
        }
        # 本地签名
        sign_tx = owner.sign_transaction(approve_tx_dict)
        # 发送交易
        tx_hash = web3.eth.send_raw_transaction(sign_tx.raw_transaction)
        # 等待链上响应回执并校验
        receipt = web3.eth.wait_for_transaction_receipt(tx_hash)
        assert receipt["status"] == 1, "授权失败"
        #第2次授权，金额为0
        # 构造授权交易体
        approve_tx_dict = {
            "from": owner.address,
            "to": erc20_contract.address,  # 目标：ERC20合约地址（不是接收方）
            "value": web3.to_wei(0, "ether"),  # ETH金额为0，代币金额在data里
            "gas": 100000,
            "maxPriorityFeePerGas": web3.to_wei(2, "gwei"),
            "maxFeePerGas": web3.to_wei(40, "gwei"),
            "nonce": web3.eth.get_transaction_count(owner.address),
            "chainId": 31337,  # hardhad节点
            "type": "0x2",  # 标记为 EIP1559 交易
            "data":
                erc20_contract.functions.approve(spender, 0).build_transaction({"from": owner.address,"gas":10000})[
                    "data"]
        }
        # 本地签名
        sign_tx = owner.sign_transaction(approve_tx_dict)
        # 发送交易
        tx_hash = web3.eth.send_raw_transaction(sign_tx.raw_transaction)
        # 等待链上响应回执并校验
        receipt = web3.eth.wait_for_transaction_receipt(tx_hash)
        assert receipt["status"] == 1, "授权失败"
        #查看链上额度
        allowance_amount = erc20_contract.functions.allowance(owner.address, spender).call()
        assert allowance_amount == 0, "取消授权失败"
        # 构造授权转账交易体
        transfer_from_tx_dict = {
            "from": spender,  # 被授权方
            "to": erc20_contract.address,  # 目标：ERC20合约地址（不是接收方）
            "value": web3.to_wei(0, "ether"),  # ETH金额为0，代币金额在data里
            "gas": gas,
            "maxPriorityFeePerGas": web3.to_wei(maxPriorityFeePerGas, "gwei"),
            "maxFeePerGas": web3.to_wei(maxFeePerGas, "gwei"),
            "nonce": web3.eth.get_transaction_count(spender),
            "chainId": 31337,  # hardhad节点
            # 关键：编码transfer方法调用（to地址 + 代币最小单位金额）
            "data": erc20_contract.functions.transferFrom(owner.address, recipient_address,
                                                          transfer_amount).build_transaction(
                {"from": spender, "gas": gas})["data"],
            "type": "0x2"
        }
        tx_dict_str = json.dumps(transfer_from_tx_dict, indent=2, ensure_ascii=False)
        with allure.step("授权转账交易请求信息"):
            allure.attach(tx_dict_str, "交易体", attachment_type=allure.attachment_type.JSON)
        # 本地签名
        transfer_from_sign_tx = spender_obj.sign_transaction(transfer_from_tx_dict)
        # 发送交易
        try:
            web3.eth.send_raw_transaction(transfer_from_sign_tx.raw_transaction)
        except Exception as e:
            err_msg = str(e)
            # 匹配 ERC20 余额不足
            assert "reverted" in err_msg




    elif mark == "repeat":
        # 预估gas量-approve
        approve_temp_tx = {
            "from": owner.address,
            "to": erc20_contract.address,
            "value": web3.to_wei(0, "ether"),
            "data":
                erc20_contract.functions.approve(spender, amount_approve).build_transaction({"from": owner.address})[
                    "data"],
            "maxPriorityFeePerGas": web3.to_wei(2, "gwei"),
            "maxFeePerGas": web3.to_wei(40, "gwei"),
            "chainId": 31337

        }
        approve_gas_limit = web3.eth.estimate_gas(approve_temp_tx) + 500
        # 构造授权交易体
        approve_tx_dict = {
            "from": owner.address,
            "to": erc20_contract.address,  # 目标：ERC20合约地址（不是接收方）
            "value": web3.to_wei(0, "ether"),  # ETH金额为0，代币金额在data里
            "gas": approve_gas_limit,
            "maxPriorityFeePerGas": web3.to_wei(2, "gwei"),
            "maxFeePerGas": web3.to_wei(40, "gwei"),
            "nonce": web3.eth.get_transaction_count(owner.address),
            "chainId": 31337,  # hardhad节点
            "type": "0x2",  # 标记为 EIP1559 交易
            "data":
                erc20_contract.functions.approve(spender, amount_approve).build_transaction({"from": owner.address})[
                    "data"]
        }
        # 本地签名
        sign_tx = owner.sign_transaction(approve_tx_dict)
        # 发送交易
        tx_hash = web3.eth.send_raw_transaction(sign_tx.raw_transaction)
        # 等待链上响应回执并校验
        receipt = web3.eth.wait_for_transaction_receipt(tx_hash)
        assert receipt["status"] == 1, "授权失败"
        # 构造授权转账交易体
        transfer_from_tx_dict = {
            "from": spender,  # 被授权方
            "to": erc20_contract.address,  # 目标：ERC20合约地址（不是接收方）
            "value": web3.to_wei(0, "ether"),  # ETH金额为0，代币金额在data里
            "gas": gas,
            "maxPriorityFeePerGas": web3.to_wei(maxPriorityFeePerGas, "gwei"),
            "maxFeePerGas": web3.to_wei(maxFeePerGas, "gwei"),
            "nonce": web3.eth.get_transaction_count(spender),
            "chainId": 31337,  # hardhad节点
            # 关键：编码transfer方法调用（to地址 + 代币最小单位金额）
            "data": erc20_contract.functions.transferFrom(owner.address, recipient_address,
                                                          transfer_amount).build_transaction(
                {"from": spender, "gas": gas})["data"],
            "type": "0x2"
        }
        tx_dict_str = json.dumps(transfer_from_tx_dict, indent=2, ensure_ascii=False)
        with allure.step("授权转账交易请求信息"):
            allure.attach(tx_dict_str, "交易体", attachment_type=allure.attachment_type.JSON)
        # 本地签名
        transfer_from_sign_tx = spender_obj.sign_transaction(transfer_from_tx_dict)
        # 发送交易
        transfer_from_tx_hash = web3.eth.send_raw_transaction(transfer_from_sign_tx.raw_transaction)
        receipt = web3.eth.wait_for_transaction_receipt(transfer_from_tx_hash)
        if receipt["status"] == 1:
            try:
                # 重复发送同一笔交易
                web3.eth.send_raw_transaction(transfer_from_sign_tx.raw_transaction)
            except Exception as e:
                err_msg = str(e).lower()
                with allure.step("交易-异常响应断言"):
                    assert "nonce too low" in err_msg, f"非预期异常：{err_msg}"


    elif mark == "invalid_sign":
        # 预估gas量-approve
        approve_temp_tx = {
            "from": owner.address,
            "to": erc20_contract.address,
            "value": web3.to_wei(0, "ether"),
            "data":
                erc20_contract.functions.approve(spender, amount_approve).build_transaction({"from": owner.address})[
                    "data"],
            "maxPriorityFeePerGas": web3.to_wei(2, "gwei"),
            "maxFeePerGas": web3.to_wei(40, "gwei"),
            "chainId": 31337

        }
        approve_gas_limit = web3.eth.estimate_gas(approve_temp_tx) + 500
        # 构造授权交易体
        approve_tx_dict = {
            "from": owner.address,
            "to": erc20_contract.address,  # 目标：ERC20合约地址（不是接收方）
            "value": web3.to_wei(0, "ether"),  # ETH金额为0，代币金额在data里
            "gas": approve_gas_limit,
            "maxPriorityFeePerGas": web3.to_wei(2, "gwei"),
            "maxFeePerGas": web3.to_wei(40, "gwei"),
            "nonce": web3.eth.get_transaction_count(owner.address),
            "chainId": 31337,  # hardhad节点
            "type": "0x2",  # 标记为 EIP1559 交易
            "data":
                erc20_contract.functions.approve(spender, amount_approve).build_transaction({"from": owner.address})[
                    "data"]
        }
        # 本地签名
        sign_tx = owner.sign_transaction(approve_tx_dict)
        # 发送交易
        tx_hash = web3.eth.send_raw_transaction(sign_tx.raw_transaction)
        # 等待链上响应回执并校验
        receipt = web3.eth.wait_for_transaction_receipt(tx_hash)
        assert receipt["status"] == 1, "授权失败"
        # 构造授权转账交易体
        transfer_from_tx_dict = {
            "from": spender,  # 被授权方
            "to": erc20_contract.address,  # 目标：ERC20合约地址（不是接收方）
            "value": web3.to_wei(0, "ether"),  # ETH金额为0，代币金额在data里
            "gas": gas,
            "maxPriorityFeePerGas": web3.to_wei(maxPriorityFeePerGas, "gwei"),
            "maxFeePerGas": web3.to_wei(maxFeePerGas, "gwei"),
            "nonce": web3.eth.get_transaction_count(spender),
            "chainId": 31337,  # hardhad节点
            # 关键：编码transfer方法调用（to地址 + 代币最小单位金额）
            "data": erc20_contract.functions.transferFrom(owner.address, recipient_address,
                                                          transfer_amount).build_transaction(
                {"from": spender, "gas": gas})["data"],
            "type": "0x2"
        }
        tx_dict_str = json.dumps(transfer_from_tx_dict, indent=2, ensure_ascii=False)
        with allure.step("授权转账交易请求信息"):
            allure.attach(tx_dict_str, "交易体", attachment_type=allure.attachment_type.JSON)
        # 本地签名
        transfer_from_sign_tx = spender_obj.sign_transaction(transfer_from_tx_dict)
        raw_tx = transfer_from_sign_tx.raw_transaction
        illegal_r = b"\xff" * 32  # 非法r值（超过曲线阶）
        modify_raw_tx = raw_tx[:-65] + illegal_r + raw_tx[-33:]  # 替换r字段（前32字节签名）
        with allure.step("交易请求信息"):
            allure.attach(f"{modify_raw_tx}","篡改信息", attachment_type=allure.attachment_type.TEXT)
        try:
            web3.eth.send_raw_transaction(modify_raw_tx)
        except Exception as e:
            err_msg = str(e).lower()
            with allure.step("交易-异常响应断言"):
                # 匹配验签失败或gas异常（兜底）
                assert any(k in err_msg for k in ["invalid", "signature", "hash mismatch", "requires at least"]), \
                    f"非预期异常：{err_msg}"

    elif mark == "fee_wrong":
        # 预估gas量-approve
        approve_temp_tx = {
            "from": owner.address,
            "to": erc20_contract.address,
            "value": web3.to_wei(0, "ether"),
            "data":
                erc20_contract.functions.approve(spender, amount_approve).build_transaction({"from": owner.address})[
                    "data"],
            "maxPriorityFeePerGas": web3.to_wei(2, "gwei"),
            "maxFeePerGas": web3.to_wei(40, "gwei"),
            "chainId": 31337

        }
        approve_gas_limit = web3.eth.estimate_gas(approve_temp_tx) + 500
        # 构造授权交易体
        approve_tx_dict = {
            "from": owner.address,
            "to": erc20_contract.address,  # 目标：ERC20合约地址（不是接收方）
            "value": web3.to_wei(0, "ether"),  # ETH金额为0，代币金额在data里
            "gas": approve_gas_limit,
            "maxPriorityFeePerGas": web3.to_wei(2, "gwei"),
            "maxFeePerGas": web3.to_wei(40, "gwei"),
            "nonce": web3.eth.get_transaction_count(owner.address),
            "chainId": 31337,  # hardhad节点
            "type": "0x2",  # 标记为 EIP1559 交易
            "data":
                erc20_contract.functions.approve(spender, amount_approve).build_transaction({"from": owner.address})[
                    "data"]
        }
        # 本地签名
        sign_tx = owner.sign_transaction(approve_tx_dict)
        # 发送交易
        tx_hash = web3.eth.send_raw_transaction(sign_tx.raw_transaction)
        # 等待链上响应回执并校验
        receipt = web3.eth.wait_for_transaction_receipt(tx_hash)
        assert receipt["status"] == 1, "授权失败"
        # 构造授权转账交易体
        transfer_from_tx_dict = {
            "from": spender,  # 被授权方
            "to": erc20_contract.address,  # 目标：ERC20合约地址（不是接收方）
            "value": web3.to_wei(0, "ether"),  # ETH金额为0，代币金额在data里
            "gas": gas,
            "maxPriorityFeePerGas": web3.to_wei(maxPriorityFeePerGas, "gwei"),
            "maxFeePerGas": web3.to_wei(maxFeePerGas, "gwei"),
            "nonce": web3.eth.get_transaction_count(spender),
            "chainId": 31337,  # hardhad节点
            # 关键：编码transfer方法调用（to地址 + 代币最小单位金额）
            "data": erc20_contract.functions.transferFrom(owner.address, recipient_address,
                                                          transfer_amount).build_transaction(
                {"from": spender, "gas": gas})["data"],
            "type": "0x2"
        }
        tx_dict_str = json.dumps(transfer_from_tx_dict, indent=2, ensure_ascii=False)
        with allure.step("授权转账交易请求信息"):
            allure.attach(tx_dict_str, "交易体", attachment_type=allure.attachment_type.JSON)
        # 本地签名
        transfer_from_sign_tx = spender_obj.sign_transaction(transfer_from_tx_dict)
        try:
            # 发送交易
            web3.eth.send_raw_transaction(transfer_from_sign_tx.raw_transaction)
        except Exception as e:
            err_msg = str(e).lower()
            with allure.step("交易-异常响应断言"):
                assert "maxpriorityfeepergas" in str(e) or "bigger" in err_msg, f"非预期异常{err_msg}"





