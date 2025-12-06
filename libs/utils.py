# coding = utf-8
# author = fufu
"""
统一工具函数
目的：避免代码重复
"""
from pathlib import Path
import yaml
import re




def load_yaml(filepath: str):
    '''
    加载yaml文件
    :param filepath: 相对于项目根路径的目录
    :return: yaml解析后的字典
    '''
    base_path = Path(__file__).parent.parent #项目根目录
    full_path = base_path / filepath #完整文件路径
    #首先判断文件路径是否存在，不存在抛异常
    if not full_path.exists():
        raise FileNotFoundError(f"文件路径不存在：{full_path}")
    #文件路径存在，读取yaml文件内容
    with open(full_path, 'r', encoding='utf-8') as f:
        return  yaml.safe_load(f)



def render_placeholders(obj, context):
    """
    递归替换数据中的占位符： 3种形式
      - {{key}} → 来自 context（如 random_username）
      - {{key1.key2}}  → 来自 context 嵌套上下文（如 sell.username）
      - ${en.key} → 来自 context  获取的环境变量，前缀en.
    """
    if isinstance(obj, dict):
        return {k: render_placeholders(v, context) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [render_placeholders(item, context) for item in obj]
    elif isinstance(obj, str):
        def replace_match(match):
            path = match.group(1)  # 如 "buyer_reg.username"
            keys = path.split('.')  # ['buyer_reg', 'username']
            value = context
            try:
                for key in keys:
                    if isinstance(value, dict) and key in value:
                        value = value[key]
                    else:
                        raise KeyError(f"路径 '{path}' 中的键 '{key}' 未找到")
                return str(value)
            except (KeyError, TypeError) as e:
                raise KeyError(f"占位符 '{{{{{path}}}}}' 解析失败: {e}")
        # 允许占位符包含字母、数字、下划线、点号
        return re.sub(r"\{\{([a-zA-Z_]\w*(?:\.[a-zA-Z_]\w*)*)\}\}", replace_match, obj)
    else:
        return obj


def parse_erc721_error(exception) -> dict:
    """
    极简核心版：转字典 → 按嵌套键取值 → 索引切分错误码
    """

    ERROR_MAP= {
                "0x8456cb59": "Caller is not the contract owner",  # 铸造-非合约所有者
                "0xcd23a68c": "Caller is not owner or approved",  # 销毁-无操作权限
                "0x0b4261a6": "Token ID does not exist",  # 销毁-TokenID不存在
                "0x8c1b0028": "Caller is not owner nor approved",  # 授权-无权限
                "0x179aa88a": "Cannot approve to current owner",  # 授权-授权给当前所有者
                "0x7c44a4e0": "Transfer from incorrect owner",  # 转账-转出非所有者
                "0x289a3a9c": "Receiver does not support ERC721",  # 转账-接收方不支持ERC721
                "0x4b807420": "Transfer to zero address is prohibited",  # 转账-禁止转零地址
                "0x02571792": "Owner query for nonexistent token" ,  # 查询-查询不存在的Token
                "0x73c6ac6e":  "Token ID already minted (OpenZeppelin v5+)" ,#铸造-TokenID重复
                "0x3C44CdDd": "ERC721InsufficientApproval" #授权操作者无权限
            }
    try:
        # 直接取异常信息字符串
        msg = str(exception)
        if '0x' in msg:
            # 找到第一个 0x 的位置，往后取10位（0x + 8个字符）
            start = msg.find('0x')
            if start != -1 and start + 10 <= len(msg):
                error_selector = msg[start:start + 10]
                return {
                "error_code": error_selector,
                "message": ERROR_MAP.get(error_selector, f"未知错误：{error_selector}")
            }
        else:
            return {"error_code": "N/A", "message": "未找到错误数据"}
    except Exception as ex:
        return {"error_code": "N/A", "message": f"解析失败：{str(ex)}"}