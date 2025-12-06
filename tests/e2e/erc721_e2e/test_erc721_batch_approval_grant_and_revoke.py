# test_erc721_batch_approval_grant_and_revoke.py
# coding =utf-8
# author =fufu
# date: 2025.12.05
import pytest
import allure
import os
from libs.utils import load_yaml,render_placeholders,parse_erc721_error
import random
from web3.exceptions import Web3RPCError
#读取yaml用例,转为字典
case = load_yaml("yaml_case/e2e/test_erc721_batch_approval_grant_and_revoke.yaml")

#获取环境变量的值 + 获取动态随机变量，避免私钥直接暴露+避免yaml硬编码
context ={
    "en":{
    "deployer_private_key": os.getenv("deployer_private_key"),
    "address1_private_key": os.getenv("address1_private_key"),
    "address2_private_key": os.getenv("address2_private_key"),
    "address3_private_key": os.getenv("address3_private_key")
    },
    "random_num_1": random.randint(10000,99999),
    "random_num_2": random.randint(10000,99999)
}



# 模块级上下文字典，存储动态生成的参数
context_dict ={}

def test_erc721_batch_approval_grant_and_revoke(web3,erc721_contract):
    """
    erc721合约主流程场景测试： --by fufu 2025.12.05
    gas_type :EIP-1559
    1-2创建多个nft
    3-4 创世地址将nft转移给其他地址
    5 nft所有者批量授权(全部授权)给其他第三方地址
    6 查询地址已全部授权
    7 被授权者授权转账，将nft转给其他第三方_成功
    8 nft所有者取消批量授权
    9 查询地址已取消批量授权
    10 被授权者授权转账，将nft转给其他第三方_失败
    :param case: yaml用例
    :param web3: 一个连接本地hardhat实例
    :param erc721_contract: 合约
    :return:
    """
    #allure报告动态标题
    allure.dynamic.title(case["name"])
    allure.dynamic.description(case["name"])
    #获取yaml steps 所有操作步骤：字典列表{[],[]}
    steps_data = case["steps"]
    mint_count=0
    #for循环依此遍历所有操作步骤数据
    for step_data in steps_data:
        #allure记录测试步骤
        with allure.step(step_data["step"]):
            #获取yaml场景用例里步骤标志action,跟据action走场景测试
            action = step_data["action"]

            #----------步骤1&2:创世地址铸造多个nft-----------
            if action == "mint":
                """
                # -- by fufu -- by fufu -- by fufu -- by fufu -- by fufu -- by fufu 
                # 渲染逻辑说明：yaml 环境变量&随机变量+ 上下文动态变量 全部渲染时，会报错，因为上下文变量找不到对应key。
                # 渲染方案-设计步骤1：渲染引擎渲染变量，每一步分别渲染
                # 渲染方案-设计步骤2：对上下文变量渲染前，需要先将上下文动态变量作为键+对应值 传到上下文空字典（2种方法：用键赋值 +append）
                # 渲染方案-设计步骤3：将context字典 **解包后作为键值对整体插入到上下文字典，再整体渲染  
                """
                mint_count += 1
                step_data = render_placeholders(step_data, context)
                print(step_data)
                # 构建交易体 -mint
                tx_mint =erc721_contract.functions.mint(
                    step_data["address"],
                    int(step_data["token_id"]),
                    step_data["meta_uri"]
                ).build_transaction({
                    "from":step_data["address"],
                    "nonce": web3.eth.get_transaction_count(step_data["address"]),
                    "gas": 200000,
                    "gasPrice": web3.eth.gas_price
                }
                )
                # 构建完整字典，用于allure报告记录请求体
                dict_mint = {
                    "from": step_data["address"],
                    "nonce": web3.eth.get_transaction_count(step_data["address"]),
                    "gas": 200000,
                    "gas_price": web3.eth.gas_price,
                    "to":step_data["address"],
                    "meta_uri": step_data["meta_uri"],
                    "token_id": step_data["token_id"]
                }
                with allure.step(f"铸造交易请求详情"):
                    allure.attach(str(dict_mint),"交易体字典详情",attachment_type=allure.attachment_type.JSON)
                print(dict_mint)
                #本地签名
                signed_tx = web3.eth.account.sign_transaction(tx_mint,step_data["PRIVATE_KEY"])
                #发送mint请求
                tx_hash_mint = web3.eth.send_raw_transaction(signed_tx.raw_transaction)
                #等待交易回执
                receipt = web3.eth.wait_for_transaction_receipt(tx_hash_mint)
                with allure.step("断言"):
                    # 对交易回执中内置基础信息断言
                    assert receipt["status"] == 1,f"交易失败"
                    #对交易回执中的logs日志信息进行解码读取。
                    mint_event = erc721_contract.events.Transfer().process_receipt(receipt)
                    assert mint_event[0]["args"]["to"] == step_data["address"]
                    assert mint_event[0]["args"]["tokenId"] == int(step_data["token_id"])
                    context_dict[f"token_id_{mint_count}"] = step_data["token_id"]
                    print(context_dict)

            # ----------3&4 地址所有者将nft转给其他接受地址-----------
            elif action == "transferFrom_owner":

                #先将环境变量和上下文变量组成新字典；再 将yaml中参数变量渲染到对应值. by fufu
                context_full = {**context,**context_dict}
                step_data = render_placeholders(step_data, context_full)
                tx_transfer = erc721_contract.functions.transferFrom(
                    step_data["address"],
                    step_data["to_address"],
                    int(step_data[f"token_id"])
                ).build_transaction({
                    "from": step_data["address"],
                    "nonce": web3.eth.get_transaction_count(step_data["address"]),
                    "gas": 200000,
                    "gasPrice": web3.eth.gas_price
                })
                # 构建完整字典，用于allure报告记录请求体
                dict_transfer = {
                    "from": step_data["address"],
                    "nonce": web3.eth.get_transaction_count(step_data["address"]),
                    "gas": 200000,
                    "gas_price": web3.eth.gas_price,
                    "to":  step_data["to_address"],
                    f"token_id": step_data["token_id"]
                }
                with allure.step("转账交易请求详情"):
                    allure.attach(str(dict_transfer), "交易体字典详情", attachment_type=allure.attachment_type.JSON)
                # 本地签名
                signed_tx = web3.eth.account.sign_transaction(tx_transfer, step_data["PRIVATE_KEY"])
                # 发送transfer请求
                tx_hash_transfer = web3.eth.send_raw_transaction(signed_tx.raw_transaction)
                # 等待交易回执
                receipt = web3.eth.wait_for_transaction_receipt(tx_hash_transfer)
                with allure.step("断言"):
                    # 对交易回执中内置基础信息断言
                    assert receipt["status"] == 1,f"交易失败"
                   # 对交易回执日志事件断言
                    transfer_event = erc721_contract.events.Transfer().process_receipt(receipt)
                    assert transfer_event[0]["args"]["to"] == step_data["to_address"]
                    assert transfer_event[0]["args"]["from"] == step_data["address"]
                    assert transfer_event[0]["args"]["tokenId"] == int(step_data["token_id"])

            # ----------5 nft所有者批量授权(全部授权)给其他第三方地址-----------
            elif action == "ApprovalForAll_true":
                # 先将环境变量和上下文变量组成新字典；再 将yaml中参数变量渲染到对应值. by fufu
                context_full = {**context, **context_dict}
                step_data = render_placeholders(step_data, context_full)
                tx_approve_all = erc721_contract.functions.setApprovalForAll(
                    step_data["operator_address"],
                    True
                ).build_transaction({
                    "from": step_data["address"],
                    "nonce": web3.eth.get_transaction_count(step_data["address"]),
                    "gas": 200000,
                    "gasPrice": web3.eth.gas_price
                })
                # 构建完整字典，用于allure报告记录请求体
                dict_approve_all = {
                    "from": step_data["address"],
                    "nonce": web3.eth.get_transaction_count(step_data["address"]),
                    "gas": 200000,
                    "gas_price": web3.eth.gas_price,
                    "to": step_data["operator_address"]
                }
                with allure.step("授权交易请求详情"):
                    allure.attach(str(dict_approve_all), "交易体字典详情", attachment_type=allure.attachment_type.JSON)
                # 本地签名
                signed_tx = web3.eth.account.sign_transaction(tx_approve_all, step_data["PRIVATE_KEY"])
                # 发送approve请求
                tx_hash_approve = web3.eth.send_raw_transaction(signed_tx.raw_transaction)
                # 等待交易回执
                receipt = web3.eth.wait_for_transaction_receipt(tx_hash_approve)
                with allure.step("断言"):
                    # 对交易回执中内置基础信息断言
                    assert receipt["status"] == 1, f"交易失败"
                    # 对交易回执日志事件断言
                    transfer_event = erc721_contract.events.ApprovalForAll().process_receipt(receipt)
                    assert transfer_event[0]["args"]["operator"] == step_data["operator_address"]
                    assert transfer_event[0]["args"]["owner"] == step_data["address"]
                    assert transfer_event[0]["args"]["approved"] == True
            # ----------6 查询地址已全部授权-----------
            elif action == "isApprovedForAll_true":
                context_full = {**context, **context_dict}
                step_data = render_placeholders(step_data, context_full)
                result = erc721_contract.functions.isApprovedForAll(step_data["input"]["address"], step_data["input"]["operator_address"]).call()
                with allure.step("断言"):
                    assert result == step_data["expected"]["result"]

            # ----------7 被授权者授权转账，将nft1转给其他第三方_成功-----------
            elif action == "transferFrom_approve_success":
                context_full = {**context, **context_dict}
                step_data = render_placeholders(step_data, context_full)
                tx_transfer_approve = erc721_contract.functions.transferFrom(
                    step_data["owner_address"],
                    step_data["to_address"],
                    int(step_data["token_id"])
                ).build_transaction({
                    "from": step_data["operator_address"],
                    "nonce": web3.eth.get_transaction_count(step_data["operator_address"]),
                    "gas": 200000,
                    "gasPrice": web3.eth.gas_price
                })
                dict_transfer_approve = {
                    "from": step_data["owner_address"],
                    "operator": step_data["operator_address"],
                    "nonce": web3.eth.get_transaction_count(step_data["operator_address"]),
                    "gas": 200000,
                    "gasPrice": web3.eth.gas_price,
                    "to": step_data["to_address"],
                    "token_id": step_data["token_id"]
                }
                with allure.step("授权转账请求详情"):
                    allure.attach(str(dict_transfer_approve), "交易体字典详情", attachment_type=allure.attachment_type.JSON)
                # 本地签名
                signed_tx = web3.eth.account.sign_transaction(tx_transfer_approve, step_data["PRIVATE_KEY"])
                # transferFrom请求
                tx_hash_transfer_approve = web3.eth.send_raw_transaction(signed_tx.raw_transaction)
                # 等待交易回执
                receipt = web3.eth.wait_for_transaction_receipt(tx_hash_transfer_approve)
                with allure.step("断言"):
                    # 对交易回执中内置基础信息断言
                    assert receipt["status"] == 1, f"交易失败"
                    # 对交易回执日志事件断言
                    transfer_approve_event = erc721_contract.events.Transfer().process_receipt(receipt)
                    assert transfer_approve_event[0]["args"]["from"] == step_data["owner_address"]
                    assert transfer_approve_event[0]["args"]["to"] == step_data["to_address"]
                    assert transfer_approve_event[0]["args"]["tokenId"] == int(step_data["token_id"])

            # ----------8 nft所有者取消批量授权-----------
            elif action == "ApprovalForAll_false":
                # 先将环境变量和上下文变量组成新字典；再 将yaml中参数变量渲染到对应值. by fufu
                context_full = {**context, **context_dict}
                step_data = render_placeholders(step_data, context_full)
                tx_approve_all = erc721_contract.functions.setApprovalForAll(
                    step_data["operator_address"],
                    False
                ).build_transaction({
                    "from": step_data["address"],
                    "nonce": web3.eth.get_transaction_count(step_data["address"]),
                    "gas": 200000,
                    "gasPrice": web3.eth.gas_price
                })
                # 构建完整字典，用于allure报告记录请求体
                dict_approve_all = {
                    "from": step_data["address"],
                    "nonce": web3.eth.get_transaction_count(step_data["address"]),
                    "gas": 200000,
                    "gas_price": web3.eth.gas_price,
                    "to": step_data["operator_address"]
                }
                with allure.step("授权交易请求详情"):
                    allure.attach(str(dict_approve_all), "交易体字典详情", attachment_type=allure.attachment_type.JSON)
                # 本地签名
                signed_tx = web3.eth.account.sign_transaction(tx_approve_all, step_data["PRIVATE_KEY"])
                # 发送approve请求
                tx_hash_approve = web3.eth.send_raw_transaction(signed_tx.raw_transaction)
                # 等待交易回执
                receipt = web3.eth.wait_for_transaction_receipt(tx_hash_approve)
                with allure.step("断言"):
                    # 对交易回执中内置基础信息断言
                    assert receipt["status"] == 1, f"交易失败"
                    # 对交易回执日志事件断言
                    transfer_event = erc721_contract.events.ApprovalForAll().process_receipt(receipt)
                    assert transfer_event[0]["args"]["operator"] == step_data["operator_address"]
                    assert transfer_event[0]["args"]["owner"] == step_data["address"]
                    assert transfer_event[0]["args"]["approved"] == False
            # ----------9:查询地址已取消批量授权-----------
            elif action == "isApprovedForAll_false":
                context_full = {**context, **context_dict}
                step_data = render_placeholders(step_data, context_full)
                result = erc721_contract.functions.isApprovedForAll(step_data["input"]["address"],
                                                                    step_data["input"]["operator_address"]).call()
                with allure.step("断言"):
                    assert result == step_data["expected"]["result"]
            # ----------10:被授权者授权转账，将nft2转给其他第三方_失败-----------
            elif action == "transferFrom_approve_false":
                context_full = {**context, **context_dict}
                step_data = render_placeholders(step_data, context_full)
                tx_transfer_approve = erc721_contract.functions.transferFrom(
                    step_data["owner_address"],
                    step_data["to_address"],
                    int(step_data["token_id"])
                ).build_transaction({
                    "from": step_data["operator_address"],
                    "nonce": web3.eth.get_transaction_count(step_data["operator_address"]),
                    "gas": 200000,
                    "gasPrice": web3.eth.gas_price
                })
                dict_transfer_approve = {
                    "from": step_data["owner_address"],
                    "operator": step_data["operator_address"],
                    "nonce": web3.eth.get_transaction_count(step_data["operator_address"]),
                    "gas": 200000,
                    "gasPrice": web3.eth.gas_price,
                    "to": step_data["to_address"],
                    "token_id": step_data["token_id"]
                }
                with allure.step("授权转账请求详情"):
                    allure.attach(str(dict_transfer_approve), "交易体字典详情", attachment_type=allure.attachment_type.JSON)
                # 本地签名
                signed_tx = web3.eth.account.sign_transaction(tx_transfer_approve, step_data["PRIVATE_KEY"])
                # transferFrom请求
                try:
                    web3.eth.send_raw_transaction(signed_tx.raw_transaction)
                except Exception as e:
                    with allure.step("断言"):
                        assert parse_erc721_error(str(e))["message"] == "ERC721InsufficientApproval"








