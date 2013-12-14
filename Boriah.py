# coding: utf-8

from collections import OrderedDict
from math import log

import arff

class NumeralAttribute(object):
    '''Class que implemente um atributo numeral'''

    def __init__(self, _type, _distribution, minimal, maximal, d):
        self.data_type = _type
        self.distribution = _distribution
        self.minimal = minimal
        self.maximal = maximal
        self.d = d


class NominalAttribute(object):
    '''Class que implemente um atributo nominal'''

    def __init__(self, _type, _categories, _distribution, d, N):
        self.data_type = _type
        self.categories = _categories
        self.distribution = _distribution
        self._d = d
        self._N = N

    def values(self, categoryX, categoryY):
        d = self._d
        nk = len(self.categories)
        fkXk = self.distribution[categoryX]
        fkYk = self.distribution[categoryY]
        N = self._N
        pkXk = 1.0 * fkXk / N
        pkYk = 1.0 * fkYk / N

        return d, nk, fkXk, fkYk, N, pkXk, pkYk

class Attributes(object):
    '''Classe que gera metodos para cada atributo'''

    def __init__(self, arff_attributes, data):
        self._arff_attributes = arff_attributes
        self._data = data

        self._d = len(arff_attributes)
        self._N = len(data)

        for attribute, info in arff_attributes:
            _dic = {}
            if type(info) == list:
                data_type = 'NOMINAL'
                categories = info
                distr = self.__distribution(attribute)
                attr = NominalAttribute(data_type, categories,
                                        distr, self._d, self._N)
                _dic = attr
            else:
                data_type = info
                _dist = self.__distribution(attribute)
                _dist = sorted(_dist.iteritems(), key=lambda x: x[0])
                distribution = OrderedDict(_dist)
                minimal = distribution.keys()[0]
                maximal = distribution.keys()[-1]
                attr = NumeralAttribute(data_type, distr,
                                        minimal, maximal, self._d)
                _dic = attr

            if attribute == 'class':
                setattr(self.__class__, attribute + '_', _dic)
            else:
                setattr(self.__class__, attribute, _dic)

    def __distribution(self, attribute):
        attributes = [item[0] for item in self._arff_attributes]
        attr_index = attributes.index(attribute)
        _dic = OrderedDict()

        if type(self._arff_attributes[attr_index][1]) == list:
            for item in self._arff_attributes[attr_index][1]:
                _dic[item] = 0

        for line in self._data:
            value = line[attr_index]
            if value in _dic:
                _dic[value] += 1
            else:
                _dic[value] = 1
        return _dic


class Boriah(object):
    '''Classe que calcula os índices de similaridade entre dois objetos'''

    def __init__(self, fp):
        self.arff = arff.load(open(fp))

        self.attributes = [item[0] if item[0] != 'class' else 'class_'
                           for item in self.arff['attributes']]
        self.data = self.arff['data']
        self.relation = self.arff['relation']
        self.description = self.arff['description']
        self.attribute = Attributes(self.arff['attributes'], self.data)

    def values(self, attribute, categoryX, categoryY):
        method = getattr(self.attribute, attribute)
        return method.values(categoryX, categoryY)

    def compare(self, itemX, itemY, method_name):

        comparison_list = []
        for index, values in enumerate(zip(itemX, itemY)):
            valueX, valueY = values[0], values[1]
            attribute = self.attributes[index]

            method = getattr(self.attribute, attribute)

            result = 0
            if method.data_type == 'NOMINAL':

                method = getattr(self, '_Boriah__comp_' + method_name)
                result = method(attribute, valueX, valueY)
            else:
                method = getattr(self, '_Boriah__comp_numbers')
                result = method(attribute, valueX, valueY)

            #print valueX, valueY, result
            comparison_list.append(result)
        return sum(comparison_list)#, comparison_list


    def __comp_numbers(self, attribute, valueX, valueY):
        method = getattr(self.attribute, attribute)
        _max = 1.0 * max(valueX, valueY)
        _min = 1.0 * min(valueX, valueY)
        total = method.maximal - method.minimal
        result = 1 - ((_max - _min) / total)
        d = method.d
        wk = 1.0 / d
        return wk * result


    def __comp_overlap(self, attr, categoryX, categoryY):

        #Get values relatedo to categories and attribute
        d, nk, fkXk, fkYk, N, pkXk, pkYk = self.values(attr, categoryX, categoryY)

        #Define weight
        wk = 1.0 / d

        #Define rule of thumb
        result = 1.0 if categoryX == categoryY else 0

        #Return value by weight
        return wk * result

    def __comp_eskin(self, attr, categoryX, categoryY):

        #Get values relatedo to categories and attribute
        d, nk, fkXk, fkYk, N, pkXk, pkYk = self.values(attr, categoryX, categoryY)

        #Define weight
        wk = 1.0 / d

        #Define rule of thumb
        result = 1.0 if categoryX == categoryY else (nk**2) / (nk**2 + 2)

        #Return value by weight
        return wk * result

    def __comp_iof(self, attr, categoryX, categoryY):

        #Get values relatedo to categories and attribute
        d, nk, fkXk, fkYk, N, pkXk, pkYk = self.values(attr, categoryX, categoryY)

        #Define weight
        wk = 1.0 / d

        #Define rule of thumb
        result = 1.0 if categoryX == categoryY else 1.0 / ( 1 + log(fkXk) * log(fkYk))

        #Return value by weight
        return wk * result

    def __comp_of(self, attr, categoryX, categoryY):

        #Get values relatedo to categories and attribute
        d, nk, fkXk, fkYk, N, pkXk, pkYk = self.values(attr, categoryX, categoryY)

        #Define weight
        wk = 1.0 / d

        #Define rule of thumb
        result = 1.0 if categoryX == categoryY else 1.0 / ( 1 + log(N / fkXk) * log(N / fkYk))

        #Return value by weight
        return wk * result

    def __comp_lin(self, attr, categoryX, categoryY):

        #Get values relatedo to categories and attribute
        print self.values(attr, categoryX, categoryY)
        d, nk, fkXk, fkYk, N, pkXk, pkYk = self.values(attr, categoryX, categoryY)

        #Define weight
        wk = 1.0 / d

        #Define rule of thumb
        result = 2.0 * log(pkXk) if categoryX == categoryY else 2.0 * log(pkXk + pkYk)

        #Return value by weight
        return wk * result
