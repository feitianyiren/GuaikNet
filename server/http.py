import tornado.ioloop
import tornado.web
import logging

from gevent import monkey
monkey.patch_all()

class MainHandler(tornado.web.RequestHandler):
    def get(self, *args, **kwargs):
        try:
            logging.debug(str(self.request.remote_ip)+"\n"+"-"*80+"\n"+str(self.request.body)+"\n"+"-"*80)
            self.application.analysis.decrypt_http(self.request.body,self)
        except Exception as e: logging.error(str(e))

    def post(self, *args, **kwargs):
        try:
            logging.debug(str(self.request.remote_ip)+"\n"+"-"*80+"\n"+str(self.request.body)+"\n"+"-"*80)
            self.application.analysis.decrypt_http(self.request.body,self)
        except Exception as e: logging.error(str(e))

def make_app():
    return tornado.web.Application([
        (r"/", MainHandler),
    ])

class Http():
    def __init__(self, port, analysis):
        self._port = port
        self._analysis = analysis

    def start(self):
        app = make_app()
        app.analysis = self._analysis
        app.listen(self._port)
        tornado.ioloop.IOLoop.current().start()
