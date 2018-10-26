import http
from multiprocessing import Process
import platform
import os,sys
from application import gm
from utils import log
import logging
from rpc import RpcManager
import datetime


DEBUG = logging.DEBUG
INFO = logging.INFO
WARN = logging.WARNING
ERROR = logging.ERROR

class Server():
    def __init__(self,level):
        self._http_pool = []
        self._http_list = []
        self._log_level = level
        self.init_log()

    def init_log(self):
        date = datetime.datetime.now()
        filename = "./log/"+str(date.year)+'-'+str(date.month)+'-'+str(date.day)+".log"
        gm.set("logging",log.Log(filename))
        gm.get("logging").setLevel(self._log_level)

    def active_rpc(self, host, port, vhost, user, passwd):
        if gm.has_key("rpc"):
            logging.warning("rpc server existed...")
            return
        gm.set("rpc",RpcManager(host, port, vhost, user, passwd))
        gm.get("rpc").start()

    def gen_http(self, port, analysis):
        http_obj = http.Http(port, analysis)
        self._http_list.append(http_obj)
        return http_obj

    def gen_http_process(self, start_port, count, analysis):
        for port in range(start_port,start_port+count):
            self.gen_http(port, analysis)

    def start(self,background=False):
        sysstr = platform.system()
        if sysstr == 'Linux' and background:
            dirname, filename = os.path.split(os.path.abspath(sys.argv[0]))
            daemon(dirname)

        for http_obj in self._http_list:
            p = Process(target=http_obj.start,args=())
            self._http_pool.append(p)
            p.start()

        for p in self._http_pool:
            p.join()

        if gm.has_key("rpc"):
            for p in gm.get("rpc").process():
                p.join()
