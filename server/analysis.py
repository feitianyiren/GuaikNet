import json
import logging
import os
import re
import importlib
from base.analysis import AnalysisBase

class Analysis(AnalysisBase):
    def _get_action_map(self):
        app_map = {}
        app_list = []
        path = os.path.join(os.path.dirname(__file__), "../works")
        for dirpath,dirnames,filenames in os.walk(path):
            if dirnames:
                app_list = dirnames
                break
        for app in app_list:
            m_map = {}
            path = os.path.join(os.path.dirname(__file__), "../works/"+app)
            for dirpath,dirnames,filenames in os.walk(path):
                for filename in filenames:
                    if re.match(r'(^\w+)\.py$',filename) and filename != "__init__.py":
                        m_map[filename[0:-3]] = importlib.import_module("works.{}.{}".format(app,filename[0:-3]))
            app_map[app] = m_map
        return app_map


    def __init__(self, version):
        self._version = version
        self._app_map = self._get_action_map()

    def decrypt_http(self,data,ctx):
        head_fields = ["protocol","version","action","content"]
        protocols = ["json"]
        try:
            data = json.loads(data)
            for field in head_fields:
                if field not in data.keys():
                    logging.warning("head fields error")
                    return None
            if data["protocol"] not in protocols:
                logging.warning("protocol error")
                return None
            if data["version"] != self._version:
                logging.warning("version error")
                return None
            if type(data["content"]) != dict:
                logging.warning("content type error")
                return None

            action = data["action"].split(".")
            if len(action) != 2:
                logging.warning("action format error")
                return None
            action = getattr(self._app_map[action[0]][action[1]],"handler")
            if action:
                action(data["content"],ctx)

        except Exception as e:
            logging.error(str(e))
