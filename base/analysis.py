from abc import ABCMeta, abstractmethod

class AnalysisBase():
    __metaclass__ = ABCMeta
    def __init__(self, version):
        pass

    @abstractmethod
    def _get_action_map(self):
        pass

    @abstractmethod
    def decrypt_http(self,data,ctx):
        pass
