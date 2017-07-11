from werkzeug.wrappers import Request


# WSGI 调度框架入口
def wsgi_app(app, environ, start_response):
    # 解析请求头
    request = Request(environ)

    # 处理响应
    response = app.dispatch_request(request)

    # 返回给服务器
    return response(environ, start_response)
