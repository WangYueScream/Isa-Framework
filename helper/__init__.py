import re


def list_filter(obj, func):
    for item in obj:
        if not func(item):
            return False
    return True


def check_host(host):
    if host == '0.0.0.0':
        return True
    host_tmp = host.split(".")
    return \
        len(host_tmp) == 4 and \
        1 <= int(host_tmp[0]) <= 223 and \
        list_filter(host_tmp[1:3], lambda x: 0 <= int(x) <= 255) and \
        1 <= int(host_tmp[-1]) <= 254


def check_port(port):
    if 0 <= port <= 65535:
        return True
    return False


def match_args(rule):
    pattern = r'<(.*?)>'
    comp = re.compile(pattern)
    rules = rule.split(r"/")[1:]
    ret = []
    for r in rules:
        ret.append(comp.search(r).groups()[0])

    return ret


def parse_static_key(key):
    return key.split(".")[-1]



