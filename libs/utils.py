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

