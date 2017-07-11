import json
import os

from werkzeug.serving import run_simple
from werkzeug.wrappers import Request, Response

from cbweb.exceptions import InvalidHost, InvalidPort, EndpointExist, InvalidRequestMethod
from cbweb.helper import check_host, check_port, parse_static_key
from cbweb.template_engine.__init import render_template
from cbweb.wsgi_adapter import wsgi_app
from cbweb.session import session, create_session_id
from cbweb.route import Route


ERROR_MAP = {
    '404': Response('<h1>404 Not Found<h1>', content_type='text/html', status=404)
}


# 处理函数数据结构
class ExecFuncMap:
    def __init__(self, func, func_type, **options):
        self.func = func
        self.options = options
        self.func_type = func_type


# 框架主体
class CWApp:
    template_folder = None
    static_folder = None

    def __init__(self, template_folder='template', static_folder='static', session_path='.session'):
        self.host = '127.0.0.1'    # 应用绑定的主机
        self.port = 5000    # 应用监听的端口
        self.url_maps = {}    # 存放 URL 与 Endpoint 的映射
        self.view_functions = {}    # 存放 Endpoint 与请求处理函数的映射
        self.static_maps = {}    # 存放 URL 与 静态资源的映射
        self.debug = False    # 调试模式
        self.reload = False    # 是否重加载
        self.domain = ''    # 应用主域 URL
        self.route = Route(self)    # 路由
        self.threaded = False
        self.session_path = session_path

        CWApp.template_folder = os.path.join(os.getcwd(), template_folder)    # 类变量，静态页面文件夹
        CWApp.static_folder = os.path.join(os.getcwd(), static_folder)    # 类变量，静态资源文件夹

        self.template_folder = CWApp.template_folder    # 实例变量，静态页面文件夹
        self.static_folder = CWApp.static_folder    # 实例变量，静态资源文件夹

    # 重载 setattr
    def __setattr__(self, key, value):
        """ 当为 debug 或者 reload 赋值时，直接赋值到两个变量上 """

        if key in ['debug', 'reload']:
            object.__setattr__(self, 'debug', value)
            object.__setattr__(self, 'reload', value)
        object.__setattr__(self, key, value)

    # 添加路由规则
    def add_url_rule(self, url, view_func=None, func_type='view', endpoint=None, **options):

        # 如果 Endpoint 未命名，使用处理函数的名字
        if endpoint is None:
            endpoint = view_func.__name__

        # 抛出 Endpoint 已存在异常
        if endpoint in self.view_functions and func_type != 'static':
            raise EndpointExist

        # 添加 URL 与 Endpoint 映射
        self.url_maps[url] = endpoint

        # 添加 Endpoint 与请求处理函数映射
        self.view_functions[endpoint] = ExecFuncMap(view_func, func_type, **options)

    # 添加视图规则
    def add_view(self, url, view_class, endpoint):
        self.add_url_rule(url, view_func=view_class.as_view(endpoint), func_type='view')

    # 添加静态资源
    def add_source(self, path):
        with open(path, 'r') as f:
            rep = f.read()
        key = parse_static_key(path)
        self.static_maps[key] = rep

    # 应用启动入口
    def run(self, **options):

        # 加载配置参数
        for key, value in options.items():
            if value is not None:
                self.__setattr__(key, value)

        # 检查主机是否有效
        self.__throw_host_error()

        # 检查端口是否有效
        self.__throw_port_error()

        # 建立主域 URL
        self.domain = 'http://' + self.host + ':' + str(self.port)

        # 映射静态资源
        self.add_static_rule(self.static_folder)

        # 映射静态资源处理函数
        self.view_functions['static'] = ExecFuncMap(func=self.dispatch_static, func_type='static')

        # 加载本地缓存 session 记录
        if not os.path.exists(self.session_path):
            os.mkdir(self.session_path)
        session.set_storage_path(self.session_path)
        session.load_local_session()

        # 启动
        run_simple(self.host, self.port, self, use_debugger=self.debug, use_reloader=self.reload, threaded=self.threaded)

    # 静态资源调度入口
    def dispatch_static(self, static_path):
        key = parse_static_key(static_path)
        if key in self.static_maps:
            if key == 'css':
                doc_type = 'text/css'
            elif key == 'js':
                doc_type = 'text/js'
            else:
                doc_type = 'text/plain'
            return Response(self.static_maps[key], content_type=doc_type)
        else:
            return ERROR_MAP['404']

    # 应用请求处理函数调度入口
    def dispatch_request(self, request):
        # 获取请求对应的 Endpoint
        url = "/" + "/".join(request.url.split("/")[3:])

        if url.find('static') == 1 and url.index('static') == 1:
            endpoint = 'static'
        else:
            endpoint = self.url_maps.get(url, None)

        # 如果 Endpoint 不存在 返回 404
        if endpoint is None:
            return ERROR_MAP['404']

        # 获取 Endpoint 对应的执行函数
        view_function = self.view_functions[endpoint]

        if 'session_id' not in request.cookies:
            headers = {'set-cookie': 'session_id=%s' % create_session_id(), 'Server': 'CCWEB 0.1'}
        else:
            headers = {'Server': 'CCWEB 0.1'}


        # 判断执行函数类型
        if view_function.func_type == 'route':
            """ 路由处理 """

            # 判断请求方法是否支持
            if request.method in view_function.options.get('methods'):
                """ 路由处理结果 """
                argscount = view_function.func.__code__.co_argcount
                if argscount > 0:
                    rep = view_function.func(request)
                else:
                    rep = view_function.func()
            else:
                """ 未知请求方法 """

                raise InvalidRequestMethod
                #return Response('<h1>Unknown or unsupported method</h1>', content_type='text/html')
        elif view_function.func_type == 'view':
            """ 视图处理结果 """

            rep = view_function.func(request)
        elif view_function.func_type == 'static':
            """ 静态逻辑处理 """

            return view_function.func(url)
        else:
            """ 未知类型处理 """

            return Response('<h1>Unknown function type</h1>', content_type='text/html; charset=UTF-8', headers=headers, status=403)

        status = 200
        content_type = 'text/html'
        
        if isinstance(rep, tuple):
            kind = rep[-1]
            if kind == 'redirect':
                url = rep[0]
                status = rep[1]
                response = Response('<script> window.location.href = "%s"</script>' % url, status=status, content_type='text/html')
                response.headers['Location'] = url
                return response
            elif kind == 'file':
                filename = rep[0]
                file_content = rep[1]
                response = Response(file_content, content_type='text/file')
                response.headers['Content-Length'] = len(file_content)
                response.headers['Content-Disposition'] = 'attachment; filename="%s"' % filename
                return response
            else:
                return ERROR_MAP['404']
        elif isinstance(rep, dict) or isinstance(rep, list) and isinstance(rep[0], dict):
            rep = json.dumps(rep)
            content_type = 'application/json'
        else:
            rep = str(rep)

        return Response(rep, content_type='%s; charset=UTF-8' % content_type, headers=headers, status=status)

    # WSGI 调度框架入口
    def wsgi_app(self, environ, start_response):
        # 解析请求头
        request = Request(environ)

        # 获取请求处理结果
        response = self.dispatch_request(request)

        # 返回给 WSGI
        return response(environ, start_response)

    # 蓝图注册
    def register_blueprint(self, blueprint):
        # 添加对应蓝图中的视图
        name = blueprint.__name__()
        for line in blueprint.url_maps:
            self.add_view(line['url'], line['view'], name + '.' + line['endpoint'])

    # 加载静态资源
    def add_static_rule(self, path):
        if not os.path.exists(path):
            return
        for line in os.listdir(path):
            if os.path.isdir(os.path.join(path, line)):
                self.add_static_rule(os.path.join(path, line))
            else:
                self.add_source(os.path.join(path, line))

    # App 调度入口
    def __call__(self, environ, start_response):
        return wsgi_app(self, environ, start_response)

    # 主机取值检查
    def __throw_host_error(self):
        if not check_host(self.host):
            raise InvalidHost()

    # 端口取值检查
    def __throw_port_error(self):
        if not check_port(self.port):
            raise InvalidPort()
        

def render_file(file_path, file_name=None):
    content = None
    if os.path.exists(file_path):
        with open(file_path, 'rb') as f:
            content = f.read()
    
    if filename is None:
        filename = file_path.split("/")[-1]
    file_size = os.path.getsize(file_path)
            
    return filename, content, 'file'


def redirect(url, status_code=302):
    return url, status_code, 'redirect'


# 默认模版引擎
def simple_template(path, **options):
    return render_template(CWApp, path, **options)

# jinja模版引擎
jinja_render = None
