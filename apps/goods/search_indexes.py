from haystack import indexes

from apps.goods.models import Goods


class GoodsIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=True)
    price = indexes.FloatField(model_attr='price')

    def get_model(self):
        return Goods
