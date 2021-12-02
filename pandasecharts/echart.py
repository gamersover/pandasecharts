import pandas as pd
from .chart_tool import get_pie, get_bar, get_bar3d, get_line, get_scatter
from .chart_tool import timeline_decorator, by_decorator

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
            by=None,
            legend_opts={},
            timeline=None,
            timeline_opts={}):
        df = self._obj.copy()
        df[x] = df[x].astype(str)

        td = timeline_decorator(timeline, timeline_opts)
        bd = by_decorator(by=by)
        return td(bd(get_pie))(
            df=df, 
            x=x, 
            y=y, 
            title=title, 
            subtitle=subtitle, 
            label_show=label_show, 
            agg_func=agg_func, 
            legend_opts=legend_opts
        )

    def bar(self,
            x="",
            ys="",
            xaxis_name=None,
            yaxis_name="",
            title="",
            subtitle="",
            agg_func=None,
            stack_view=False,
            label_show=False,
            reverse_axis=False,
            by=None,
            timeline=None,
            timeline_opts={}):
        df = self._obj.copy()
        df[x] = df[x].astype(str)

        if xaxis_name is None:
            xaxis_name = x

        if not isinstance(ys, list):
            ys = [ys]
        
        td = timeline_decorator(timeline, timeline_opts)
        bd = by_decorator(by=by)
        return td(bd(get_bar))(
            df=df, 
            x=x, 
            ys=ys, 
            xaxis_name=xaxis_name,
            yaxis_name=yaxis_name,
            title=title, 
            subtitle=subtitle, 
            agg_func=agg_func, 
            stack_view=stack_view,
            reverse_axis=reverse_axis,
            label_show=label_show, 
        )
        
    def bar3d(self,
              x="",
              y="",
              z="",
              by=None,
              title="",
              subtitle="",
              timeline=None,
              timeline_opts={}):
        df = self._obj.copy()
        df[x] = df[x].astype(str)

        td = timeline_decorator(timeline, timeline_opts)
        bd = by_decorator(by=by)
        return td(bd(get_bar3d))(
            df=df, 
            x=x, 
            y=y,
            z=z, 
            title=title, 
            subtitle=subtitle, 
        )

    def line(self,
             x="",
             ys="",
             xtype=None,
             xaxis_name=None,
             yaxis_name="",
             title="",
             subtitle="",
             agg_func=None,
             smooth=False,
             label_show=False,
             by=None,
             timeline=None,
             timeline_opts={}):
        df = self._obj.copy()
        df[x] = df[x].astype(str)

        if xaxis_name is None:
            xaxis_name = x

        if not isinstance(ys, list):
            ys = [ys]

        td = timeline_decorator(timeline, timeline_opts)
        bd = by_decorator(by=by)
        return td(bd(get_line))(
            df=df, 
            x=x, 
            ys=ys,
            xtype=xtype, 
            xaxis_name=xaxis_name,
            yaxis_name=yaxis_name,
            title=title, 
            subtitle=subtitle, 
            agg_func=agg_func, 
            smooth=smooth,
            label_show=label_show, 
        )

    def scatter(self,
                x="",
                ys="",
                xtype=None,
                xaxis_name=None,
                yaxis_name="",
                title="",
                subtitle="",
                agg_func=None,
                label_show=False,
                by=None,
                timeline=None,
                timeline_opts={}):
        df = self._obj.copy()
        df[x] = df[x].astype(str)
        
        if xaxis_name is None:
            xaxis_name = x

        if not isinstance(ys, list):
            ys = [ys]

        td = timeline_decorator(timeline, timeline_opts)
        bd = by_decorator(by=by)
        return td(bd(get_scatter))(
            df=df, 
            x=x, 
            ys=ys, 
            xtype=xtype,
            xaxis_name=xaxis_name,
            yaxis_name=yaxis_name,
            title=title, 
            subtitle=subtitle, 
            agg_func=agg_func, 
            label_show=label_show, 
        )


@pd.api.extensions.register_series_accessor("echart")
class SeriesEcharts:
    def __init__(self, series_obj):
        self._obj = series_obj
        # TODO: series 需要区分数据是离散类型还是连续类型
        # TODO: series 只支持画单个变量的分布图，对于连续变量可以使用freedman_diaconis规则获取bins个数，参考自seaborn里的distplot
        # TODO: bar和line可以支持显示density还是count，类似numpy.histogram

    def pie():
        ...
