# coding: utf-8
from elasticsearch_dsl.connections import connections
ES_HOST = "10.10.0.247:9200"
# ES_HOST = {"host": "192.168.10.190:9200"}
connections.configure(default={"hosts": ES_HOST})
REDIS_HOST = ""
REDIS_PASSWORD = ""

# REDIS_HOST = "127.0.0.1"
# REDIS_PASSWORD = ""

ES_INDEX = "mxx_zjac_t2"
ES_DOC_TYPE = "doc"

