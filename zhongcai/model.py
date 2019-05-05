# coding: utf-8
from elasticsearch_dsl.utils import ObjectBase, AttrList
from elasticsearch_dsl.document import DocType as _DocType, DOC_META_FIELDS
from elasticsearch_dsl.field import InnerObjectWrapper as _InnerObjectWrapper
from elasticsearch_dsl.field import Keyword, Text, Date, Integer, Float, Nested as _Nested, Object as _Object
from elasticsearch_dsl.analysis import analyzer, tokenizer

from six import iteritems

import config


class SerializeEmptyValueMixin(ObjectBase):
    """
    我们使用的ES是5.x版本，没有保存空值的可选参数(在6.x的版本官方才提供)
    而我们需要保存空值，避免接口返回的字段存在缺失
    所以自己来提供一个Mixin，重写父类接口的to_dict方法，来保存空值。
    """

    def to_dict(self, skip_empty=False):
        """
        :param skip_empty: 是否跳过空值
        """
        out = {}
        for k, v in iteritems(self._d_):
            try:
                f = self._doc_type.mapping[k]
            except KeyError:
                pass
            else:
                if f._coerce:
                    v = f.serialize(v)

            if isinstance(v, AttrList):
                v = v._l_

            if skip_empty:
                # don't serialize empty values
                # careful not to include numeric zeros
                if v in ([], {}, None):
                    continue

            out[k] = v
        return out


class DocType(SerializeEmptyValueMixin, _DocType):
    def to_dict(self, include_meta=False, skip_empty=False):
        """重写to_dict配合上面的存储空值Mixin"""

        d = super(DocType, self).to_dict(skip_empty=skip_empty)
        if not include_meta:
            return d

        meta = dict(
            ('_' + k, self.meta[k])
            for k in DOC_META_FIELDS
            if k in self.meta
        )

        # in case of to_dict include the index unlike save/update/delete
        if 'index' in self.meta:
            meta['_index'] = self.meta.index
        elif self._doc_type.index:
            meta['_index'] = self._doc_type.index

        meta['_type'] = self._doc_type.name
        meta['_source'] = d
        return meta


class InnerObjectWrapper(SerializeEmptyValueMixin, _InnerObjectWrapper):
    """同样是为了保存空值，要使用Nested字段或Object字段请使用这个包装类"""


class Nested(_Nested):
    def _serialize(self, data):
        if isinstance(data, dict):
            return data
        return super(Nested, self)._serialize(data)


class Object(_Object):
    def _serialize(self, data):
        if isinstance(data, dict):
            return data
        return super(Object, self)._serialize(data)


class MXXZjacDoc(DocType):
    caseId = Keyword()
    ctime = Keyword()
    timeStamp = Keyword()
    applicant = Keyword()
    respondent = Nested(doc_class=InnerObjectWrapper,
                        properties={
                           "name": Keyword(),
                           "certAddress": Keyword(),
                           "phone": Keyword(),
                           "email": Keyword(),
                           "otherAddress": Keyword(),
                           "idcard": Keyword(),
                           "card_front": Text(),
                           "card_nfront": Text(),
                        })

    text = """
    借款年利率:Annual interest rate of borrowing
    合同金额:Contract amount
    放款金额:Loan amount
    合同签订时间:  
    借款开始时间:Borrowing start time
    借款结束时间:End of loan time
    借款时常:Borrowing often
    借款时长单位:Borrowing time unit
    违约时间:Default time
    尚欠本金:Still owed principal
    尚欠利息:Interest owed
    仲裁协议签订时间:Arbitration agreement time
    是否分期（分批）:Whether to stage (batch)
    居间方:Intermediary party
    借款用途:Use of the loan
    还款方式:Repayment
    是否涉外:Whether it is foreign-related
    """
    caseInfo = Object(doc_class=InnerObjectWrapper,
                      properties={
                          "annualInterestOfBorrowing": Float(),
                          "contractAmount": Float(),
                          "loanAmount": Float(),
                          "contractTime ": Keyword(),
                          "borrowingStartTime": Keyword(),
                          "borrowingEndTime": Keyword(),
                          "borrowingOften": Integer(),
                          "borrowingTimeUnit": Keyword(),
                          "defaultTime": Keyword(),
                          "stillOwedPrincipal": Float(),
                          "interestOwed": Float(),
                          "arbitrationAgreementTime": Keyword(),
                          "whetherStaging": Keyword(),
                          "intermediaryParty": Keyword(),
                          "usageLoan": Keyword(),
                          "repaymentWay": Keyword(),
                          "whetherForeign": Keyword(),
                      })

    contentiousAmount = Float()

    class Meta:
        index = config.ES_INDEX
        doc_type = config.ES_DOC_TYPE

    @classmethod
    def make_doc(cls, caseId, ctime, timeStamp, applicant, respondent, caseInfo, contentiousAmount):
        doc_obj = cls()
        doc_obj.meta.id = caseId
        doc_obj.caseId = caseId
        doc_obj.ctime = ctime
        doc_obj.timeStamp = timeStamp
        doc_obj.applicant = applicant
        doc_obj.respondent = respondent
        doc_obj.respondent = caseInfo
        doc_obj.respondent = contentiousAmount
        doc_obj.save()
        return doc_obj.to_dict(include_meta=False)


if __name__ == '__main__':

    print(MXXZjacDoc.init())


