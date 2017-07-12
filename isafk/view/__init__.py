# 视图基类
class View:
    # 支持的请求方法
    methods = None

    # 请求处理函数映射
    methods_meta = None

    # 视图处理函数调度入口
    def dispatch_request(self, request, *args, **option):
        raise NotImplementedError

    # 生成视图处理函数
    @classmethod
    def as_view(cls, name, *class_args, **class_kwargs):

        # 定义处理函数
        def view(*args, **kwargs):
            # 实例化视图对象
            obj = view.view_class(*class_args, **class_kwargs)

            # 返回视图处理结果
            return obj.dispatch_request(*args, **kwargs)

        # 为处理函数绑定属性
        view.view_class = cls
        view.__name__ = name
        view.__doc__ = cls.__doc__
        view.__module__ = cls.__module__
        view.methods = cls.methods
        return view


# 蓝图基类
class Blueprint:
    def __init__(self, name, url_maps):
        self.url_maps = url_maps
        self.name = name

    def __name__(self):
        return self.name
