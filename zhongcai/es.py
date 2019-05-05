# coding: utf-8
import sys
sys.path.append('./')
sys.path.append('../')

import config
import re

from elasticsearch import Elasticsearch
from elasticsearch import helpers

es = Elasticsearch([config.ES_HOST])
index_name = 'mxx_zjac'
doc_type = 'doc'
reg_tag = re.compile('|'.join(['利率', '金额', '本金', '利息']))


def es_index(body, case_id):
    """es 插入"""
    resp_obj = es.index(index=index_name, doc_type='doc', body=body, id=case_id)
    if resp_obj and resp_obj['result'] == 'created' and resp_obj['created']:
        return True
    return False


def es_search(authorize_id):
    """es 查询"""
    pass
    # result = es.search(index=index_name, body={"query": {"match": {"caseId": authorize_id}}})
    # print(json.dumps(result, ensure_ascii=False))
    # return result
    # doc_obj = es.get(index=index_name, id=authorize_id, ignore=404)
    # print(doc_obj)


def es_update(case_id):
    # doc_obj = es.get(index=index_name, id=case_id, ignore=404)
    # json_data = doc_obj['_source']
    # print(json_data)
    # for respondent in json_data['respondent']:
    #     for key in respondent:
    #         if key == 'otherAddress' and respondent[key] == '':
    #             respondent.pop('otherAddress')
    #             break
    # print(json_data)
    # result = es.update(index=index_name, doc_type='doc', body={'doc': json_data}, id=case_id)
    # print(result)

    doc_obj = es.get(index=index_name, id=case_id, ignore=404)
    json_data = doc_obj['_source']
    print(json_data)
    case_info = json_data['case_info']
    for k in case_info.keys():
        if reg_tag.search(k) and isinstance(case_info[k], str):
            case_info.update({k: eval(case_info[k])})
    print(json_data)
    result = es.update(index=index_name, doc_type='doc', body={'doc': json_data}, id=case_id)
    print(result)


def es_scan_all():
    es_result = helpers.scan(
        client=es,
        query={"term": {"applicant": {"value": "深圳市中兰德小额贷款有限责任公司"}}},
        index=index_name,
        doc_type=doc_type,
    )
    return es_result


if __name__ == '__main__':
    # es_search('68746')
    es_update('68738')
