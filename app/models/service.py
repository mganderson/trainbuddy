from ferris import BasicModel
from google.appengine.ext import ndb


class Service(BasicModel):
    title = ndb.StringProperty()
