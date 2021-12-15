import numpy as np
import pandas as pd


def infer_dtype(series):
    if pd.api.types.infer_dtype(series) == "string":
        return "category"
    else:
        return "value"


# TODO: 需支持可定制，类似pd.xxxxsize=100等可以设置全局属性，
# 数组的唯一值超过该数字，则认为变量为连续性？也许可以参考catboost怎么区分连续和离散变量
max_discrete_size = 50


# TODO: 标注该算法来自于seaborn里的distplot
def _freedman_diaconis_bins(a):
    a = np.asarray(a)
    if len(a) < 2:
        return 1
    iqr = np.subtract.reduce(np.nanpercentile(a, [75, 25]))
    h = 2 * iqr / (len(a) ** (1 / 3))
    if h == 0:
        return int(np.sqrt(a.size))
    else:
        return int(np.ceil((a.max() - a.min()) / h))


def _categorize_array(a, bins=None):
    a = np.asarray(a)
    if bins is None:
        bins = min(_freedman_diaconis_bins(a), max_discrete_size)
    _, bin_edges = np.histogram(a, bins)
    cat_a = np.digitize(a, bins=bin_edges)
    cat2region = dict(
        zip(range(1, bins+1), zip(bin_edges[:-1], bin_edges[1:])))
    region_a = [cat2region[min(c, bins)] for c in cat_a]
    return region_a
