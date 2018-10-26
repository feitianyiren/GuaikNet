import pika
import uuid
import json
import multiprocessing
import inspect
import os,sys
import logging
import re
import importlib

class RpcServer():
    def __init__(self, host, port, vhost, queue, credentials, func):
        self._connection = pika.BlockingConnection(pika.ConnectionParameters(host,port,vhost,credentials))
        self._channel = self._connection.channel()
        self._channel.queue_declare(queue = queue)
        self._channel.basic_qos(prefetch_count=1)
        self._channel.basic_consume(self.on_request, queue=queue)
        self._func = func

    def start(self):
        self._channel.start_consuming()

    def on_request(self, ch, method, props, body):
        data = json.loads(body)
        args = data["args"]
        response = self._func(*args)

        ch.basic_publish(exchange='',
                     routing_key=props.reply_to,
                     properties=pika.BasicProperties(correlation_id = \
                                                         props.correlation_id),
                     body=json.dumps(response))
        ch.basic_ack(delivery_tag = method.delivery_tag)

class RpcClient(object):
    def __init__(self, host, port, vhost, route_key, credentials):
        self._connection = pika.BlockingConnection(pika.ConnectionParameters(host,port,vhost,credentials))
        self.channel = self._connection.channel()
        result = self.channel.queue_declare(exclusive=True)
        self.callback_queue = result.method.queue
        self.channel.basic_consume(self.on_response, no_ack=True,
                                   queue=self.callback_queue)
        self._route_key = route_key

    def on_response(self, ch, method, props, body):
        if self.corr_id == props.correlation_id:
            self.response = body

    def call(self, args):
        param = json.dumps({"args":args})
        self.response = None
        self.corr_id = str(uuid.uuid4())
        self.channel.basic_publish(exchange='',
                                   routing_key=self._route_key,
                                   properties=pika.BasicProperties(
                                         reply_to = self.callback_queue,
                                         correlation_id = self.corr_id,
                                         ),
                                   body=param)
        while self.response is None:
            self._connection.process_data_events()
        return json.loads(self.response)

class RpcManager():
    def __init__(self, host, port, vhost, user, passwd):
        self._credentials = pika.PlainCredentials(user, passwd)
        self._host = host
        self._port = port
        self._vhost = vhost
        self._servers = []
        self._clients = {}
        self._serv_process = []

    def call(self,key,*args):
        if self._clients.has_key(key):
            return self._clients[key].call(args)
        else: logging.warning("rpc route_key error.")

    def process(self):
        return self._serv_process

    def start(self):
        for root,dirs,files in os.walk("./rpc"):
            for filename in files:
                if re.match(r'(^\w+)\.py$',filename) and filename != "__init__.py":
                    importlib.import_module("rpc.{}".format(filename[0:-3]))

    def print_dbg(self):
        logging.debug("servers:{}\nclients{}".format(self._servers,self._clients))

    def _rpc_server_worker(self, host, port, vhost, route_key, credentials, func):
        s = RpcServer(host, port, vhost, route_key, credentials, func)
        self._servers.append(s)
        s.start()

    def route(self):
        def _change_func(func):
            route_key = "{}.{}".format(inspect.getmodule(func).__name__.split('.')[1],func.__name__)
            self._clients[route_key] = RpcClient(self._host, self._port, self._vhost, route_key, self._credentials)
            p = multiprocessing.Process(target=self._rpc_server_worker,
                 args=(self._host, self._port, self._vhost, route_key, self._credentials, func))
            self._serv_process.append(p)
            p.start()
            def _new_func(self,*args):
                return func
            return _new_func
        return _change_func
