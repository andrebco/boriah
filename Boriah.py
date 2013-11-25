# coding: utf-8

from collections import OrderedDict
from math import log

import arff

class Boriah(object):
    '''Classe que calcula os índices de similaridade entre dois objetos'''

    def __init__(self, fp):
        self.arff = arff.load(open(fp))

        self.attributes = [item[0] for item in self.arff['attributes']]
        self.data = self.arff['data']
        self.relation = self.arff['relation']
        self.description = self.arff['description']

        for attribute, info in self.arff['attributes']:
            _dic = {}
            if type(info) == list:
                _dic['type'] = 'NOMINAL'
                _dic['categories'] = info
                _dic['distribution'] = self.__distribution(attribute)
            else:
                _dic['type'] = info
                _dist = self.__distribution(attribute)
                _dist = sorted(_dist.iteritems(), key=lambda x: x[0])
                _dic['distribution'] = OrderedDict(_dist)
                _dic['min'] = _dic['distribution'].keys()[0]
                _dic['max'] = _dic['distribution'].keys()[-1]
            setattr(self.__class__, 'attribute_' + attribute, _dic)


    def __distribution(self, attribute):
        attr_index = self.attributes.index(attribute)
        _dic = OrderedDict()

        if type(self.arff['attributes'][attr_index][1]) == list:
            for item in self.arff['attributes'][attr_index][1]:
                _dic[item] = 0

        for line in self.data:
            value = line[attr_index]
            if value in _dic:
                _dic[value] += 1
            else:
                _dic[value] = 1
        return _dic

    def compare(self, item_0, item_1, method_name):

        comparison_list = []
        for index, values in enumerate(zip(item_0, item_1)):
            v0, v1 = values[0], values[1]
            field = self.attributes[index]

            method = getattr(self, 'attribute_' + field)
            result = 0
            if method['type'] == 'NOMINAL':
                method = getattr(self, '_Boriah__comp_' + method_name)
                result = method(field, v1, v0)
            else:
                method = getattr(self, '_Boriah__comp_numbers')
                result = method(field, v1, v0)

            comparison_list.append(result)
        return comparison_list

    def __comp_numbers(self, field, v0, v1):
        method = getattr(self, 'attribute_' + field)
        _max = 1.0 * max(v0, v1)
        _min = 1.0 * min(v0, v1)
        total = method['max'] - method['min']
        return 1 - ((_max - _min) / total)

    def __comp_overlap(self, field, v0, v1):
        method = getattr(self, 'attribute_' + field)

        d = len(self.attributes)
        wk = 1.0 / d

        result = 0
        if v0 == v1:
            result = 1.0
        else:
            result = 0
        return wk * result

    def __comp_eskin(self, field, v0, v1):
        method = getattr(self, 'attribute_' + field)

        d = len(self.attributes)
        wk = 1.0 / d

        nk = len(method['categories'])

        result = 0
        if v0 == v1:
            result = 1.0
        else:
            result = (nk**2) / (nk**2 + 2)
        return wk * result

    def __comp_iof(self, field, v0, v1):
        method = getattr(self, 'attribute_' + field)

        d = len(self.attributes)
        wk = 1.0 / d

        nk = len(method['categories'])
        fkXk = method['distribution'][v0]
        fkYk = method['distribution'][v1]

        result = 0
        if v0 == v1:
            result = 1.0
        else:
            result = 1 / ( 1 + log(fkXk) * log(fkYk))
        return wk * result

    def __comp_of(self, field, v0, v1):
        method = getattr(self, 'attribute_' + field)

        d = len(self.attributes)
        wk = 1.0 / d

        nk = len(method['categories'])
        fkXk = method['distribution'][v0]
        fkYk = method['distribution'][v1]
        N = len(self.data)

        result = 0
        if v0 == v1:
            result = 1.0
        else:
            result = 1 / ( 1 + log(N / fkXk) * log(N / fkYk))
        return wk * result
