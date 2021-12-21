import numpy as np
import pandas as pd
from ..configs.basic_cfg import options


def infer_dtype(series):
    if pd.api.types.infer_dtype(series) == "string":
        return "category"
    else:
        return "value"


# 该算法参考https://github.com/mwaskom/seaborn/blob/master/seaborn/distributions.py#L2419
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
    if bins is not None:
        if len(a) < bins:
            return a
    if bins is None:
        bins = min(_freedman_diaconis_bins(a), options.get("max_bins"))
    _, bin_edges = np.histogram(a, bins)
    cat_a = np.digitize(a, bins=bin_edges)
    cat2region = dict(
        zip(range(1, bins+1), zip(bin_edges[:-1], bin_edges[1:])))
    region_a = [cat2region[min(c, bins)][0] for c in cat_a]
    return region_a
