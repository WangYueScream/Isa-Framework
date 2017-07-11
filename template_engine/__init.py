import os
import re


# 模版
pattern = r'{{(.*?)}}'


# 解析模版
def parse_args(obj):
    comp = re.compile(pattern)
    ret = comp.findall(obj)
    if ret:
        return ret
    else:
        return ()


# 返回模版内容
def render_template(obj, path, **options):
    content = '<h1>Not Found Template</h1>'
    path = os.path.join(obj.template_folder, path)
    if os.path.exists(path):
        with open(path, 'rb') as f:
            content = f.read().decode()
    args = parse_args(content)

    if options:
        for arg in args:
            key = arg.strip()
            content = content.replace("{{%s}}" % arg, str(options.get(key, '')))
        return content
    else:
        return content
