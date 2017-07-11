# 异常基类
class CbWebException(Exception):
    def __init__(self, message):
        self.message = message

    def __str__(self):
        return self.message


# 权限不足
class RequireRootPermission(CbWebException):
    def __init__(self):
        self.message = 'Require root index permission'


# 端口无效
class InvalidPort(CbWebException):
    def __init__(self):
        self.message = 'Invalid port value, the value must in 0~65535'


# 主机无效
class InvalidHost(CbWebException):
    def __init__(self):
        self.message = 'Invalid host value, require a valid host value'


# 不支持的请求方法
class InvalidRequestMethod(CbWebException):
    def __init__(self):
        self.message = 'Unknown or unsupported request method'


# Endpoint 存在
class EndpointExist(CbWebException):
    def __init__(self):
        self.message = 'Endpoint exist'


class TemplateError(CbWebException):
    def __init__(self, message=None):
        if message is not None:
            self.message = message
        else:
            self.message = 'Template Format Error'
