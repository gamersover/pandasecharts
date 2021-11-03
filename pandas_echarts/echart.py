import pandas as pd
from pyecharts.charts import Bar, Line, Pie
from pyecharts import options as opts
from pyecharts.commons.utils import JsCode
from pyecharts.options.global_options import TitleOpts


def get_pie(data, x, y, label_show):
    pie = (
        Pie()
        .add(str(y), data[[x, y]].values.tolist())
        .set_series_opts(
            label_opts=opts.LabelOpts(formatter="{b}:{d}%", position="inner", is_show=label_show))
    )
    return pie


@pd.api.extensions.register_dataframe_accessor("echart")
class DataFrameEcharts:
    def __init__(self, pandas_obj):
        self._obj = pandas_obj
    
    def pie(self, 
            x="brand", 
            ys="count", 
            agg_func=None, 
            label_show=False):
        # 如果有timeline的话，可能要做？
        if not isinstance(ys, list):
            ys = [ys]
        
        if agg_func is not None:
            df = self._obj.groupby(x)[ys].agg(agg_func).reset_index()
        else:
            df = self._obj.copy()
        
        pies = []
        for y in ys:
            pies.append(get_pie(df, x, y, label_show=label_show))
        if len(pies) == 1:
            pies = pies[0]
        return pies

    def bar(self, 
            x="", 
            ys="", 
            xaxis_name="", 
            yaxis_name="",
            title="",
            subtitle="", 
            agg_func=None, 
            stack_view=False, 
            label_show=False):
        if not isinstance(ys, list):
            ys = [ys]
        
        if stack_view:
            stack = ["1"]*len(ys)
        else:
            stack = [str(i) for i in range(1, len(ys)+1)]
        
        if agg_func is not None:
            df = self._obj.groupby(x)[ys].agg(agg_func).reset_index()
        else:
            df = self._obj.copy()
        
        bar = (
            Bar()
            .add_xaxis(df[x].tolist())
        )

        for y, st in zip(ys, stack):
            bar.add_yaxis(str(y), df[y].tolist(), stack=st)
        
        bar.set_series_opts(
            label_opts=opts.LabelOpts(position="right" if stack_view else "top", is_show=label_show),
        )
        bar.set_global_opts(
            xaxis_opts=opts.AxisOpts(name=xaxis_name),
            yaxis_opts=opts.AxisOpts(name=yaxis_name),
            title_opts=opts.TitleOpts(title=title, subtitle=subtitle)
        )
        return bar
    
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
        if not isinstance(ys, list):
            ys = [ys]
        
        if agg_func is not None:
            df = self._obj.groupby(x)[ys].agg(agg_func).reset_index()
        else:
            df = self._obj.copy()
        
        line = (
            Line()
            .add_xaxis(df[x].tolist())
        )

        for y in ys:
            line.add_yaxis(str(y), df[y].tolist(), is_smooth=smooth)
        
        line.set_series_opts(
            label_opts=opts.LabelOpts(is_show=label_show)
        )

        line.set_global_opts(
            xaxis_opts=opts.AxisOpts(name=xaxis_name),
            yaxis_opts=opts.AxisOpts(name=yaxis_name),
            title_opts=opts.TitleOpts(title=title, subtitle=subtitle)
        )
        return line


@pd.api.extensions.register_series_accessor("echart")
class SeriesEcharts:
    def __init__(self, series_obj):
        self._obj = series_obj
    
    def pie():
        get_pie()
        ...
