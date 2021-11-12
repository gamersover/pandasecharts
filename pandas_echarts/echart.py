import numpy as np
import pandas as pd
from pyecharts.charts import *
from pyecharts import options as opts
from pyecharts.commons.utils import JsCode

# TODO: 所有dataframe的数据需要检查类型是否为基本类型，或者能否转为基本类型
# 在画某些图时，如果ys太多，可能会不好看，可以限制一下最大显示个数，如果超过输出警告提示用户相关信息
# 所有函数的逻辑输入dataframe 输出echart

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


def _categorize_array(a, category='auto'):
    a = np.asarray(a)
    if category == 'auto':
        if a.dtype.type is np.str_:
            category = 1
        elif len(np.unique(a)) > max_discrete_size:
            category = 0
        else:
            category = 1
    
    if category == 1:
        return a
    
    if category > 0:
        cat_bins = category
    else:
        cat_bins = min(_freedman_diaconis_bins(a), max_discrete_size)
    
    _, bin_edges = np.histogram(a, cat_bins)
    cat_a = np.digitize(a, bins=bin_edges)
    cat2region = dict(zip(range(1, cat_bins+1), zip(bin_edges[:-1], bin_edges[1:])))
    region_a = [cat2region[min(c, cat_bins)] for c in cat_a]
    return region_a


@pd.api.extensions.register_dataframe_accessor("echart")
class DataFrameEcharts:
    def __init__(self, pandas_obj):
        self._obj = pandas_obj
    
    def pie(self, 
            x="", 
            y="", 
            title="",
            subtitle="",
            agg_func=None, 
            label_show=False,
            x_category='auto'):
        # x_category逻辑应该是这样的，如果auto则按照原规则，如果是int类型（注意True就是1，False就是0），则1:是category类型，0:不是category类型，>1则表示bins大小
        # TODO: 如果有timeline的话，可能要做？
        df = self._obj.copy()
        if agg_func is not None:
            df[x] = _categorize_array(df[x], x_category)
            df = df.groupby(x)[y].agg(agg_func).reset_index()
        
        pie = (
            Pie()
            .add(str(y), df[[x, y]].values)
            .set_series_opts(
                label_opts=opts.LabelOpts(formatter="{b}:{d}%", position="inner", is_show=label_show))
            .set_global_opts(
                title_opts=opts.TitleOpts(title=title, subtitle=subtitle),
                legend_opts=opts.LegendOpts(type_="scroll", pos_left="left", orient="vertical"),
            )
        )
        return pie

    def bar(self, 
            x="", 
            ys="", 
            xaxis_name="", 
            yaxis_name="",
            title="",
            subtitle="", 
            agg_func=None, 
            stack_view=False, 
            label_show=False,
            reverse_axis=False):
        # TODO: 这里x轴看看能不能改成等距显示，类似df.hist，line也类似
        # TODO: 类似df.hist 添加一个by参数，从而可以实现根据不同分类画出多个图
        df = self._obj.copy()
        if not isinstance(ys, list):
            ys = [ys]
        
        if stack_view:
            stack = ["1"]*len(ys)
        else:
            stack = [str(i) for i in range(1, len(ys)+1)]
        
        if agg_func is not None:
            df = df.groupby(x)[ys].agg(agg_func).reset_index()
        
        bar = (
            Bar()
            .add_xaxis(df[x].tolist())
        )

        for y, st in zip(ys, stack):
            bar.add_yaxis(str(y), df[y].tolist(), stack=st)
        
        bar.set_series_opts(
            label_opts=opts.LabelOpts(
                position="right" if stack_view or reverse_axis else "top", 
                is_show=label_show
            ),
        )
        bar.set_global_opts(
            xaxis_opts=opts.AxisOpts(name=xaxis_name, type_='category'),
            yaxis_opts=opts.AxisOpts(name=yaxis_name, type_='value'),
            title_opts=opts.TitleOpts(title=title, subtitle=subtitle)
        )
        if reverse_axis:
            bar.reversal_axis()
        return bar
    
    def bar3d(self,
              x="",
              y="",
              z=""):
        df = self._obj.copy()
        bar3d = (
            Bar3D()
            .add(
                "",
                data=df[[x, y, z]].values.tolist(),
                xaxis3d_opts=opts.Axis3DOpts(type_="category"),
                yaxis3d_opts=opts.Axis3DOpts(type_="category"),
                zaxis3d_opts=opts.Axis3DOpts(type_="value"),
            )
            .set_series_opts(stack="stack")
            .set_global_opts(
                visualmap_opts=opts.VisualMapOpts(max_=df[z].max())
            )
        )
        return bar3d

    def line(self, 
             x="", 
             ys="", 
             xaxis_name="", 
             yaxis_name="",
             title="",
             subtitle="", 
             agg_func=None, 
             smooth=False, 
             label_show=False):
        
        df = self._obj.copy()
        if not isinstance(ys, list):
            ys = [ys]
        
        if agg_func is not None:
            df = df.groupby(x)[ys].agg(agg_func).reset_index()
        
        line = (
            Line()
            .add_xaxis(df[x].tolist())
        )

        for y in ys:
            line.add_yaxis(str(y), df[y].tolist(), is_smooth=smooth, is_symbol_show=False)
        
        line.set_series_opts(
            label_opts=opts.LabelOpts(is_show=label_show)
        )

        # 这里需要区分xaxis的类型是value还是category
        line.set_global_opts(
            xaxis_opts=opts.AxisOpts(name=xaxis_name, type_="value"),
            yaxis_opts=opts.AxisOpts(name=yaxis_name, type_="value"),
            title_opts=opts.TitleOpts(title=title, subtitle=subtitle)
        )
        return line
    
    def scatter(self,
                x="",
                ys="",
                xaxis_name="", 
                yaxis_name="",
                title="",
                subtitle="", 
                agg_func=None,
                label_show=False):
        df = self._obj.copy()
        if not isinstance(ys, list):
            ys = [ys]
        
        if agg_func is not None:
            df = df.groupby(x)[ys].agg(agg_func).reset_index()
        
        scatter = (
            Scatter()
            .add_xaxis(df[x].tolist())
        )

        for y in ys:
            scatter.add_yaxis(str(y), df[y].tolist())
        
        scatter.set_series_opts(
            label_opts=opts.LabelOpts(is_show=label_show)
        )

        scatter.set_global_opts(
            xaxis_opts=opts.AxisOpts(name=xaxis_name, type_="value"),
            yaxis_opts=opts.AxisOpts(name=yaxis_name, type_="value"),
            title_opts=opts.TitleOpts(title=title, subtitle=subtitle)
        )
        return scatter


@pd.api.extensions.register_series_accessor("echart")
class SeriesEcharts:
    def __init__(self, series_obj):
        self._obj = series_obj
        # TODO: series 需要区分数据是离散类型还是连续类型
        # TODO: series 只支持画单个变量的分布图，对于连续变量可以使用freedman_diaconis规则获取bins个数，参考自seaborn里的distplot
        # TODO: bar和line可以支持显示density还是count，类似numpy.histogram

    def pie():
        ...
