from server import server
from server.analysis import Analysis
from server.application import gm

CUR_VERSION = "v1.01"
LEVEL = server.INFO

if __name__ == "__main__":
    server = server.Server(LEVEL)
    # server.active_rpc("rpc_host", 5672, "/", "username", "passwd")
    server.gen_http_process(8080,1,Analysis(CUR_VERSION))
    server.start(True)
