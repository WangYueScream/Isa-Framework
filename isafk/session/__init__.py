import base64
import json
import os
import time


def create_session_id():
    return base64.encodebytes(str(time.time()).encode()).decode().replace("=", '')[:-2][::-1]


def get_session_id(request):
    return request.cookies.get('session_id', '')


class AuthSession:

    @staticmethod
    def auth_session(obj, *args, **options):

        def decorator(f, request):
            if session.auth.auth_logic(request, *args, **options):
                return obj(f, request)
            else:
                return session.auth.auth_fail_callback(request, *args, **options)

        return decorator

    @staticmethod
    def auth_logic(request, *args, **options):
        raise NotImplementedError

    @staticmethod
    def auth_fail_callback(request, *args, **options):
        raise NotImplementedError


# 会话
class Session:
    def __init__(self):
        self.auth = AuthSession
        self.__header_map__ = {}
        self.__storage_path__ = None

    # 设置会话保存目录
    def set_storage_path(self, path):
        self.__storage_path__ = path

    # 更新或添加记录
    def push(self, request, item, value):
        session_id = get_session_id(request)
        if session in self.__header_map__:
            self.__header_map__[get_session_id(request)][item] = value
        else:
            self.__header_map__[session_id] = {}
            self.__header_map__[session_id][item] = value

        # 每当会话发生变化，保存到本地
        self.storage(session_id)

    # 获取当前会话的某个项
    def get_item(self, request, item):
        return self.__header_map__.get(get_session_id(request), {}).get(item, None)

    # 删除当前会话的某个项
    def pop(self, request, item, value=True):
        if item in self.__header_map__.get(get_session_id(request), {}):
            self.__header_map__.get(get_session_id(request), {}).pop(item, value)
            self.storage(get_session_id(request))

    # 获取当前会话记录
    def map(self, request):
        return self.__header_map__.get(get_session_id(request), {})

    # 加载本地会话记录
    def load_local_session(self):
        if self.__storage_path__ is not None:
            session_path_list = os.listdir(self.__storage_path__)
            for line in session_path_list:
                path = os.path.join(self.__storage_path__, line)
                with open(path, 'rb') as f:
                    rep = f.read()
                content = base64.decodebytes(rep)
                self.__header_map__[line] = json.loads(content.decode('utf8'))

    # 保存会话记录到本地
    def storage(self, session_id):
        if self.__storage_path__ is not None:
            with open(os.path.join(self.__storage_path__, session_id), 'wb') as f:
                content = json.dumps(self.__header_map__[session_id])
                f.write(base64.encodebytes(content.encode('utf8')))
                
    def __call__(self, request, *args, **kwargs):
        return self.__header_map__.get(get_session_id(request), {})


session = Session()
