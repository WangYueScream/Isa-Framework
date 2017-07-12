# 异常基类
class CbWebException(Exception):
    def __init__(self, message):
        self.message = message

    def __str__(self):
        return self.message


# 权限不足
class RequireRootPermission(CbWebException):
    def __init__(self, message='Require root permission'):
        super.__init__(message)


# 端口无效
class InvalidPortError(CbWebException):
    def __init__(self, message='Invalid port value, the value must in 0~65535'):
        super.__init__(message)


# 主机无效
class InvalidHostError(CbWebException):
    def __init__(self, message='Invalid host value, require a valid host value'):
        super.__init__(message)


# 不支持的请求方法
class InvalidRequestMethodError(CbWebException):
    def __init__(self, message='Unknown or unsupported request method'):
        super.__init__(message)


# Endpoint 存在
class EndpointExistError(CbWebException):
    def __init__(self, message='Endpoint exist'):
        super.__init__(message)


# Endpoint 存在
class URLExistError(CbWebException):
    def __init__(self, message='URL Exist'):
        super.__init__(message)


# 模版错误
class TemplateErrorError(CbWebException):
    def __init__(self, message='Template Format Error'):
        super.__init__(message)
