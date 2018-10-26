#-*-coding:utf-8-*-
"""
# 这里设定应用级别的全局对象管理
"""
class GlobalManager():
    def __init__(self):
        self._kv = {}
    def set(self, key, value):
        self._kv[key] = value
    def get(self, key):
        return self._kv[key]
    def has_key(self, key):
        return self._kv.has_key(key)

gm = GlobalManager()
