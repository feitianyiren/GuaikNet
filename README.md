# GuaikNet-怪客网络

可配置微服务的HTTP网络服务端程序

---

## ⚙️安装说明：（CentOS7）
```
yum -y install epel-release
yum -y install git
yum -y install python-tools
yum -y install python-pip
pip install --upgrade pip
pip install tornado
pip install gevent
pip install pika

pip install pymongo
pip install redis

git clone https://github.com/guaik/GuaikNet.git
cd ./GuaikNet
chmod +x ./start.sh
./start.sh

# 如果显示如下信息，证明已经成功安装并运行
# **********************************
# @ Welcome to use <GuaikNet> system
# @ website: https://bbs.guaik.org
# @ email  : luting.gu@gmail.com
# **********************************
```

## 🚀系统测试：
安装requests库
```
pip install requests
```
将项目根目录下的`client.py`文件复制到测试电脑，修改`client.py`中的`http://localhost:8080`,将其中的`localhost`改成你部署GuaikNet项目所在的服务器
地址。

然后运行：`python ./client.py`

如果返回`Welcome to use GuaikNet system`则说明系统运行正常。

---

## 📝使用说明
GuaikNet的工作目录有两个，分别是http请求的处理目录`./works`和rpc的工作目录`./rpc`。

### HTTP请求协议：
示例：`{"protocol":"json","version":"v1.01","action":"guaik.welcome","content":{}}`
> protocol: 请求协议 选项：[json, aes, rsa] (当前只使用json,aes加密和rsa加密方式还未加入)。
>
> version : 版本号，如果客户端发起请求所使用的版本号与服务器当前版本号不同，服务端将不处理请求。
>
> action  : 需要调用的服务，命名规则是以works目录为根目录: 子目录.文件名。以上面的请求"action":"guaik.welcome"为例，
将会调用guaik目录下模块名为welcome的处理函数。
>
> content : 该字段为自定义字段，按照服务端的开发文档填写。

### HTTP处理例程：(./works/guaik/welcome.py)
```
def handler(data,ctx):
    ctx.write("Welcome to use GuaiKNet system")
```
处理例程函数定义统一写成：`def handler(data,ctx): pass`，否则无法被系统解析。
> 参数：data 对应着客户端请求content字段
>
> 参数：ctx  http请求的上下文，通过该对象的`write`方法可以向客户端返回处理结果。

---

### RPC调用说明：
#### 需要安装RabbitMQ消息队列，一键安装脚本：
`curl -s -o rabbitmq.py https://raw.githubusercontent.com/guaik/GuaikInstaller/master/rabbitmq.py && python rabbitmq.py install`

RPC功能默认是关闭的，需要在./bootstrap.py文件中开启该功能：

`server.active_rpc("rpc_host", 5672, "/", "username", "passwd")`

找到该行，取消注释，填上消息队列的：(主机IP, 主机端口, 虚拟主机(vhost), 用户名, 密码)

RPC处理例程的默认目录为：`./rpc`

#### RPC处理例程调用规则：（以下是发送短信验证码的DEMO）
```
from server.application import gm
rpc = gm.get("rpc")
rpc.call("sms.send_verify_code", "+8618888888888")
```
从全局对象管理器(gm)中取出`rpc`对象，使用`rpc`对象的`call`方法，第一个参数是rpc的方法名，之后所有的参数是rpc方法对应的参数列表。原型为：
`def call(self,key,*args): ...`

方法名的规则是：`模块名.函数名`

RPC方法定义规则：（以./rpc/sms.send_verify_code为例）
```
import logging
import requests
import json
from server.application import gm
rpc = gm.get("rpc")

api_key = "your_api_key"
api_secret = "your_secret"
brand = "Guaik"

@rpc.route()
def send_verify_code(number):
    request_id = None
    try:
        data = {"api_key":api_key,"api_secret":api_secret,"number":number,"brand":brand}
        headers = {'Content-Type': 'application/json'}
        r = requests.post("https://api.nexmo.com/verify/json",headers = headers, data = json.dumps(data))
        data = json.loads(r.text)
        if data["status"] == "0":
            request_id = data["request_id"]
    except Exception as e: logging.error(e)
    return request_id
```
先从全局对象管理器gm中取出rpc对象，然后在`send_verify_code`的上方加上`@rpc.route()`注解，这时候`send_verify_code`将被注册到RpcManager中，
成为RPC处理例程。

---

## 🧙其他说明：
### ./bootstrap.py：
> LEVEL         ：当前服务器日志级别，作为Server的初始化参数传入。
> 
> CUR_VERSION   ：当前解析器的版本号，作为Analysis的参数传入，用于判断客户端发送的请求版本是否正确。

---

`server.gen_http_process(8080,1,Analysis(CUR_VERSION))`:
以上代码生成http服务进程，默认监听8080端口。1代表启动一个进程，如果该参数为4，则启动4进程依次监听8080，8081，8082，8083端口。
第三个参数传入解析器对象，该对象用于解析客户端请求并调用对应的处理例程，在该例程中存放着请求与处理例程的映射关系。也可以自定义解析器对象，
基类在`./base/analysis.py`中。

`server.start(False)`：
这边的`False`表示不以守护进程运行，如果需要以守护进程运行，则修改成`True`即可，守护进程默认只在Linux系统中生效。

---

在`./config`目录下存放着可能会用到的配置文件，`proxy.conf`为Nginx反向代理的配置文件，可以修改它并将它放到`/etc/nginx/conf.d`下，
然后重启Nginx服务使其生效。可以通过监听多个服务端口，配合Nginx实现服务端的多进程处理。
```
upstream servers {
    server localhost:8001;
    server localhost:8002;
    server localhost:8003;
    server localhost:8004;
}

server {
    listen 8080;
    location / {
        proxy_pass  http://servers;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header Host $http_host;
        proxy_set_header X-NginX-Proxy true;
        proxy_redirect off;
        # Socket.IO Support
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
   }
}
```

---

##  🎃PS：打了这么多字应该会有错别字，欢迎纠正：luting.gu@gmail.com


