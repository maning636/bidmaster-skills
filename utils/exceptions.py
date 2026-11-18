"""json_repair 的异常定义。"""


class JsonRepairError(Exception):
    """JSON 修复失败（所有候选都不可解析）。"""
