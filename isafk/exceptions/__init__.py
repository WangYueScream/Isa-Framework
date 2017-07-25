from werkzeug.wrappers import Response


# 定义公用的报头参数 Content-Type
content_type = 'text/html; charset=UTF-8'

# 异常编号与响应体的映射关系
ERROR_MAP = {
    '2': Response('<h1>E2 Not Found File</h1>', content_type=content_type, status=500),
    '13': Response('<h1>E13 No Read Permission</h1>', content_type=content_type, status=500),
    '401': Response('<h1>401 Unknown Or Unsupported Method</h1>', content_type=content_type, status=401),
    '404': Response('<h1>404 Source Not Found<h1>', content_type=content_type, status=404),
    '503': Response('<h1>503 Unknown Function Type</h1>', content_type=content_type, status=503)
}


# 框架异常基类
class SYLFkException(Exception):
    def __init__(self, code='', message='Error'):
        self.code = code
        self.message = message

    def __str__(self):
        return self.message


# 节点已存在存在
class EndpointExistsError(SYLFkException):
    def __init__(self, message='Endpoint exists'):
        super(EndpointExistsError, self).__init__(message)


# URL 已存在异常
class URLExistsError(SYLFkException):
    def __init__(self, message='URL exists'):
        super(URLExistsError, self).__init__(message)


# 文件未找到
class FileNotExistsError(SYLFkException):
    def __init__(self, code='2', message='File not found'):
        super(FileNotExistsError, self).__init__(code, message)


# 权限不足
class RequireReadPermissionError(SYLFkException):
    def __init__(self, code='13', message='Require read permission'):
        super(RequireReadPermissionError, self).__init__(code, message)


# 不支持的请求方法
class InvalidRequestMethodError(SYLFkException):
    def __init__(self, code='401', message='Unknown or unsupported request method'):
        super(InvalidRequestMethodError, self).__init__(code, message)


# 页面未找到
class PageNotFoundError(SYLFkException):
    def __init__(self, code='404', message='Source not found'):
        super(PageNotFoundError, self).__init__(code, message)


# URL 未知处理类型
class UnknownFuncError(SYLFkException):
    def __init__(self, code='503', message='Unknown function type'):
        super(UnknownFuncError, self).__init__(code, message)


def reload(code):
    def decorator(f):
        ERROR_MAP[str(code)] = f

    return decorator


# 异常捕获
def capture(f):
    def decorator(*args, **options):
        # 开始捕获异常
        try:
            # 尝试执行函数
            rep = f(*args, **options)
        except SYLFkException as e:
            # 当捕获到 SYLFkException 这个分类的异常时，判断下异常的编号，如果不为空且关联再 ERROR_MAP 中，进行对应的处理，反之接着抛出
            if e.code in ERROR_MAP and ERROR_MAP[e.code]:

                # 获取异常关联的结果
                rep = ERROR_MAP[e.code]

                # 如果异常编号小于 100，响应状态码统一设置为 500 服务端错误
                status = int(e.code) if int(e.code) >= 100 else 500

                # 判断结果是否一个响应体，如果不是，则应该就是自定义异常处理函数，调用它并封装为响应体返回
                return rep if isinstance(rep, Response) or rep is None else Response(rep(), content_type=content_type, status=status)
            else:
                # 接着抛出没有对应处理的异常
                raise e
        # 返回函数执行正常的结果
        return rep
    # 返回装饰器
    return decorator
