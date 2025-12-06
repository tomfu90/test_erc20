# erc721_e2e_single_token_lifecycle.yaml
# coding =utf-8
# author =fufu
# date: 2025.12.05
import pytest
import allure
import os
from libs.utils import load_yaml,render_placeholders
import random

#读取yaml用例,转为字典
case = load_yaml("yaml_case/e2e/erc721_e2e_single_token_lifecycle.yaml")

#获取环境变量的值 + 获取动态随机变量，避免私钥直接暴露+避免yaml硬编码
context ={
    "en":{
    "deployer_private_key": os.getenv("deployer_private_key"),
    "address1_private_key": os.getenv("address1_private_key"),
    "address2_private_key": os.getenv("address2_private_key"),
    "address3_private_key": os.getenv("address3_private_key")
    },
    "random_num": random.randint(1000,9999)
}



# 模块级上下文字典，存储动态生成的参数
context_dict ={}

def test_erc721_e2e_single_token_lifecycle(web3,erc721_contract):
    """
    erc721合约主流程场景测试： --by fufu 2025.12.05
    gas_type :legacy
    1 该nft基本信息查询：查询NFT名字符号，创世地址nft个数
    2 创世地址铸造nft
    3 查询的nft所有者信息
    4 地址所有者将nft转给其他接受地址
    5 接受地址将nft授权给其他地址
    6 根据nft查询授权关系
    7 授权转账：被授权者将nft转给新地址
    8 最终新地址将nft销毁
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
    #for循环依此遍历所有操作步骤数据
    for step_data in steps_data:
        #allure记录测试步骤
        with allure.step(step_data["step"]):
            #获取yaml场景用例里步骤标志action,跟据action走场景测试
            action = step_data["action"]
            #----------步骤1 该nft基本信息查询：查询NFT名字符号，创世地址nft个数------------
            if action == "search":
                name = erc721_contract.functions.name().call()
                symbol = erc721_contract.functions.symbol().call()
                depoly_address = step_data["address"]
                count = erc721_contract.functions.balanceOf(depoly_address).call()
                #封装结果数据，allure作为操作步骤的附件展示
                dict ={"name":name, "symbol":symbol, "count" : count }
                allure.attach(str(dict), "响应结果",allure.attachment_type.JSON)
                #allure报告添加断言结果
                with allure.step("断言结果"):
                    assert name is not None
                    assert symbol is not None
                    assert count >= 0

            #----------步骤 2创世地址铸造nft:创世地址给自己铸造-----------
            elif action == "mint":
                """
                # -- by fufu -- by fufu -- by fufu -- by fufu -- by fufu -- by fufu 
                # 渲染逻辑说明：yaml 环境变量&随机变量+ 上下文动态变量 全部渲染时，会报错，因为上下文变量找不到对应key。
                # 渲染方案-设计步骤1：渲染引擎渲染变量，每一步分别渲染
                # 渲染方案-设计步骤2：对上下文变量渲染前，需要先将上下文动态变量作为键+对应值 传到上下文空字典（2种方法：用键赋值 +append）
                # 渲染方案-设计步骤3：将context字典 **解包后作为键值对整体插入到上下文字典，再整体渲染  
                """
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
                with allure.step("铸造交易请求详情"):
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
                    #将token_id动态参数插入到上下文字典中
                    context_dict["token_id"] = step_data["token_id"]

            # ----------步骤3 创世地址将nft转给其他接受地址-----------
            elif action == "ownerOf":
                #将 yaml中 上下文动态变量 渲染到对应值。
                token_id = render_placeholders(step_data["input"]["token_id"], context_dict)
                owner = erc721_contract.functions.ownerOf(int(token_id)).call()
                with allure.step("断言结果"):
                    assert owner ==  step_data["expected"]["address"]
            # ----------4 地址所有者将nft转给其他接受地址-----------
            elif action == "transferFrom_owner":
                #先将环境变量和上下文变量组成新字典；再 将yaml中参数变量渲染到对应值. by fufu
                context_full = {**context,**context_dict}
                step_data = render_placeholders(step_data, context_full)
                tx_transfer = erc721_contract.functions.transferFrom(
                    step_data["address"],
                    step_data["to_address"],
                    int(step_data["token_id"])
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
                    "token_id": step_data["token_id"]
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

            # ----------5 接受地址将nft授权给其他地址-----------
            elif action == "approve":
                # 先将环境变量和上下文变量组成新字典；再 将yaml中参数变量渲染到对应值. by fufu
                context_full = {**context, **context_dict}
                step_data = render_placeholders(step_data, context_full)
                tx_approve = erc721_contract.functions.approve(
                    step_data["to_address"],
                    int(step_data["token_id"])
                ).build_transaction({
                    "from": step_data["address"],
                    "nonce": web3.eth.get_transaction_count(step_data["address"]),
                    "gas": 200000,
                    "gasPrice": web3.eth.gas_price
                })
                # 构建完整字典，用于allure报告记录请求体
                dict_approve = {
                    "from": step_data["address"],
                    "nonce": web3.eth.get_transaction_count(step_data["address"]),
                    "gas": 200000,
                    "gas_price": web3.eth.gas_price,
                    "to": step_data["to_address"],
                    "token_id": step_data["token_id"]
                }
                with allure.step("授权交易请求详情"):
                    allure.attach(str(dict_approve), "交易体字典详情", attachment_type=allure.attachment_type.JSON)
                # 本地签名
                signed_tx = web3.eth.account.sign_transaction(tx_approve, step_data["PRIVATE_KEY"])
                # 发送approve请求
                tx_hash_approve = web3.eth.send_raw_transaction(signed_tx.raw_transaction)
                # 等待交易回执
                receipt = web3.eth.wait_for_transaction_receipt(tx_hash_approve)
                with allure.step("断言"):
                    # 对交易回执中内置基础信息断言
                    assert receipt["status"] == 1, f"交易失败"
                    # 对交易回执日志事件断言
                    transfer_event = erc721_contract.events.Approval().process_receipt(receipt)
                    assert transfer_event[0]["args"]["approved"] == step_data["to_address"]
                    assert transfer_event[0]["args"]["owner"] == step_data["address"]
                    assert transfer_event[0]["args"]["tokenId"] == int(step_data["token_id"])
            # ----------6 根据nft查询授权关系-----------
            elif action == "getApproved":
                token_id = render_placeholders(step_data["input"]["token_id"], context_dict)
                address_approve = erc721_contract.functions.getApproved(int(token_id)).call()
                with allure.step("断言"):
                    assert address_approve ==step_data["expected"]["address"]

            # ----------7 授权转账：被授权者将nft转给新地址-----------
            elif action == "transferFrom_approve":
                context_full = {**context, **context_dict}
                step_data = render_placeholders(step_data, context_full)
                tx_transfer_approve = erc721_contract.functions.transferFrom(
                    step_data["owner_address"],
                    step_data["to_address"],
                    int(step_data["token_id"])
                ).build_transaction({
                    "from": step_data["approve_address"],
                    "nonce": web3.eth.get_transaction_count(step_data["approve_address"]),
                    "gas": 200000,
                    "gasPrice": web3.eth.gas_price
                })
                dict_transfer_approve = {
                    "from": step_data["owner_address"],
                    "operator": step_data["approve_address"],
                    "nonce": web3.eth.get_transaction_count(step_data["approve_address"]),
                    "gas": 200000,
                    "gasPrice": web3.eth.gas_price,
                    "to": step_data["to_address"],
                    "token_id": step_data["token_id"]
                }
                with allure.step("授权转账请求详情"):
                    allure.attach(str(dict_transfer_approve), "交易体字典详情", attachment_type=allure.attachment_type.JSON)
                # 本地签名
                signed_tx = web3.eth.account.sign_transaction(tx_transfer_approve, step_data["PRIVATE_KEY"])
                # 发送approve请求
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

            # ----------8 最终新地址将nft销毁-----------
            elif action == "burn":
                context_full = {**context, **context_dict}
                step_data = render_placeholders(step_data, context_full)
                tx_burn = erc721_contract.functions.burn(int(step_data["token_id"])).build_transaction({
                    "from": step_data["address"],
                    "nonce": web3.eth.get_transaction_count(step_data["address"]),
                    "gas": 200000,
                    "gasPrice": web3.eth.gas_price
                })
                dict_burn = {
                    "from": step_data["address"],
                    "nonce": web3.eth.get_transaction_count(step_data["address"]),
                    "gas": 200000,
                    "gasPrice": web3.eth.gas_price,
                    "token_id": step_data["token_id"]
                }
                with allure.step("销毁请求详情"):
                    allure.attach(str(dict_burn), "交易体字典详情",attachment_type=allure.attachment_type.JSON)
                # 本地签名
                signed_tx = web3.eth.account.sign_transaction(tx_burn, step_data["PRIVATE_KEY"])
                # 发送approve请求
                tx_hash_burn = web3.eth.send_raw_transaction(signed_tx.raw_transaction)
                # 等待交易回执
                receipt = web3.eth.wait_for_transaction_receipt(tx_hash_burn)
                with allure.step("断言"):
                    # 对交易回执中内置基础信息断言
                    assert receipt["status"] == 1, f"交易失败"
                    # 对交易回执日志事件断言
                    transfer_approve_event = erc721_contract.events.Transfer().process_receipt(receipt)
                    assert transfer_approve_event[0]["args"]["from"] == step_data["address"]
                    #转到0地址
                    assert transfer_approve_event[0]["args"]["to"] =="0x0000000000000000000000000000000000000000"
                    assert transfer_approve_event[0]["args"]["tokenId"] == int(step_data["token_id"])








