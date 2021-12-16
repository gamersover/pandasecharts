import pandas as pd
from .chart_tool import get_pie, get_bar, get_line, get_scatter
from .chart_tool import get_bar3d, get_line3d, get_scatter3d
from .chart_tool import get_boxplot, get_funnel, get_geo, get_map
from .chart_tool import timeline_decorator, by_decorator
from .data_tool import infer_dtype, _categorize_array


@pd.api.extensions.register_dataframe_accessor("echart")
class DataFrameEcharts:
    def __init__(self, pandas_obj):
        self._obj = pandas_obj

    def pie(self,
            x,
            y,
            title="",
            subtitle="",
            agg_func=None,
            label_show=False,
            label_opts={},
            legend_opts={},
            theme=None,
            by=None,
            timeline=None,
            timeline_opts={}):
        df = self._obj.copy()
        df[x] = df[x].astype(str)

        td = timeline_decorator(timeline, timeline_opts, theme)
        bd = by_decorator(by=by)
        return td(bd(get_pie))(
            df=df,
            x=x,
            y=y,
            title=title,
            subtitle=subtitle,
            label_show=label_show,
            label_opts=label_opts,
            agg_func=agg_func,
            legend_opts=legend_opts,
            theme=theme,
        )

    def bar(self,
            x,
            ys,
            xaxis_name=None,
            yaxis_name="",
            title="",
            subtitle="",
            agg_func=None,
            stack_view=False,
            label_show=False,
            label_opts={},
            reverse_axis=False,
            legend_opts={},
            theme=None,
            by=None,
            timeline=None,
            timeline_opts={}):
        df = self._obj.copy()
        # 由于dataframe的bar的x轴可以只考虑离散值，所以先按照
        # x排序，然后将x转为字符串类型，注意要在转str前排序，要不然
        # 会按照字典排序，从而造成数字排序很奇怪
        df = df.sort_values(by=x)
        df[x] = df[x].astype(str)

        if xaxis_name is None:
            xaxis_name = str(x)

        if not isinstance(ys, list):
            ys = [ys]

        td = timeline_decorator(timeline, timeline_opts, theme)
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
            label_opts=label_opts,
            legend_opts=legend_opts,
            theme=theme
        )

    def bar3d(self,
              x,
              y,
              z,
              xaxis_name=None,
              yaxis_name=None,
              zaxis_name=None,
              title="",
              subtitle="",
              visualmap=False,
              visualmap_opts={},
              theme=None,
              by=None):
        df = self._obj.copy()

        if xaxis_name is None:
            xaxis_name = str(x)
        if yaxis_name is None:
            yaxis_name = str(y)
        if zaxis_name is None:
            zaxis_name = str(z)

        bd = by_decorator(by=by)
        return bd(get_bar3d)(
            df=df,
            x=x,
            y=y,
            z=z,
            xaxis_name=xaxis_name,
            yaxis_name=yaxis_name,
            zaxis_name=zaxis_name,
            title=title,
            subtitle=subtitle,
            visualmap=visualmap,
            visualmap_opts=visualmap_opts,
            theme=theme
        )

    def line(self,
             x,
             ys,
             xtype=None,
             xaxis_name=None,
             yaxis_name="",
             title="",
             subtitle="",
             agg_func=None,
             smooth=False,
             label_show=False,
             label_opts={},
             legend_opts={},
             theme=None,
             by=None,
             timeline=None,
             timeline_opts={}):
        df = self._obj.copy()
        if xaxis_name is None:
            xaxis_name = x

        if not isinstance(ys, list):
            ys = [ys]

        td = timeline_decorator(timeline, timeline_opts, theme)
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
            label_opts=label_opts,
            legend_opts=legend_opts,
            theme=theme
        )

    def line3d(self,
               x,
               y,
               z,
               xtype=None,
               ytype=None,
               ztype=None,
               xaxis_name=None,
               yaxis_name=None,
               zaxis_name=None,
               title="",
               subtitle="",
               visualmap=False,
               visualmap_opts={},
               theme=None,
               by=None):
        df = self._obj.copy()
        if xaxis_name is None:
            xaxis_name = str(x)
        if yaxis_name is None:
            yaxis_name = str(y)
        if zaxis_name is None:
            zaxis_name = str(z)

        bd = by_decorator(by=by)
        return bd(get_line3d)(
            df=df,
            x=x,
            y=y,
            z=z,
            xtype=xtype,
            ytype=ytype,
            ztype=ztype,
            xaxis_name=xaxis_name,
            yaxis_name=yaxis_name,
            zaxis_name=zaxis_name,
            title=title,
            subtitle=subtitle,
            visualmap=visualmap,
            visualmap_opts=visualmap_opts,
            theme=theme
        )

    def scatter(self,
                x,
                ys,
                xtype=None,
                xaxis_name=None,
                yaxis_name="",
                title="",
                subtitle="",
                agg_func=None,
                label_show=False,
                label_opts={},
                legend_opts={},
                visualmap=False,
                visualmap_opts={},
                theme=None,
                by=None,
                timeline=None,
                timeline_opts={}):
        df = self._obj.copy()
        df[x] = df[x].astype(str)

        if xaxis_name is None:
            xaxis_name = x

        if not isinstance(ys, list):
            ys = [ys]

        td = timeline_decorator(timeline, timeline_opts, theme)
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
            label_opts=label_opts,
            legend_opts=legend_opts,
            visualmap=visualmap,
            visualmap_opts=visualmap_opts,
            theme=theme
        )

    def scatter3d(self,
                  x,
                  y,
                  z,
                  xtype=None,
                  ytype=None,
                  ztype=None,
                  xaxis_name=None,
                  yaxis_name=None,
                  zaxis_name=None,
                  title="",
                  subtitle="",
                  visualmap=False,
                  visualmap_opts={},
                  theme=None,
                  by=None):
        df = self._obj.copy()
        if xaxis_name is None:
            xaxis_name = str(x)
        if yaxis_name is None:
            yaxis_name = str(y)
        if zaxis_name is None:
            zaxis_name = str(z)

        bd = by_decorator(by=by)
        return bd(get_scatter3d)(
            df=df,
            x=x,
            y=y,
            z=z,
            xtype=xtype,
            ytype=ytype,
            ztype=ztype,
            xaxis_name=xaxis_name,
            yaxis_name=yaxis_name,
            zaxis_name=zaxis_name,
            title=title,
            subtitle=subtitle,
            visualmap=visualmap,
            visualmap_opts=visualmap_opts,
            theme=theme
        )

    def boxplot(self,
                ys,
                xaxis_name="",
                yaxis_name="",
                title="",
                subtitle="",
                legend_opts={},
                theme=None,
                by=None,
                timeline=None,
                timeline_opts={}):
        df = self._obj.copy()

        if not isinstance(ys, list):
            ys = [ys]

        td = timeline_decorator(timeline, timeline_opts, theme)
        bd = by_decorator(by=by)
        return td(bd(get_boxplot))(
            df=df,
            ys=ys,
            xaxis_name=xaxis_name,
            yaxis_name=yaxis_name,
            title=title,
            subtitle=subtitle,
            legend_opts=legend_opts,
            theme=theme
        )

    def funnel(self,
               x,
               y,
               title="",
               subtitle="",
               ascending=False,
               position="inner",
               legend_opts={},
               theme=None,
               by=None,
               timeline=None,
               timeline_opts={}):
        df = self._obj.copy()
        td = timeline_decorator(timeline, timeline_opts, theme)
        bd = by_decorator(by=by)
        return td(bd(get_funnel))(
            df=df,
            x=x,
            y=y,
            title=title,
            subtitle=subtitle,
            ascending=ascending,
            position=position,
            legend_opts=legend_opts,
            theme=theme
        )

    def geo(self,
            x,
            ys,
            maptype="",
            title="",
            subtitle="",
            agg_func=None,
            label_show=False,
            visualmap=False,
            visualmap_opts={},
            theme=None,
            by=None,
            timeline=None,
            timeline_opts={}):
        df = self._obj.copy()
        if not isinstance(ys, list):
            ys = [ys]

        td = timeline_decorator(timeline, timeline_opts, theme)
        bd = by_decorator(by=by)
        return td(bd(get_geo))(
            df=df,
            x=x,
            ys=ys,
            maptype=maptype,
            title=title,
            subtitle=subtitle,
            agg_func=agg_func,
            label_show=label_show,
            visualmap=visualmap,
            visualmap_opts=visualmap_opts,
            theme=theme
        )

    def map(self,
            x,
            y,
            maptype="",
            title="",
            subtitle="",
            agg_func=None,
            label_show=False,
            visualmap=False,
            visualmap_opts={},
            theme=None,
            by=None,
            timeline=None,
            timeline_opts={}):
        df = self._obj.copy()

        td = timeline_decorator(timeline, timeline_opts, theme)
        bd = by_decorator(by=by)
        return td(bd(get_map))(
            df=df,
            x=x,
            y=y,
            maptype=maptype,
            title=title,
            subtitle=subtitle,
            agg_func=agg_func,
            label_show=label_show,
            visualmap=visualmap,
            visualmap_opts=visualmap_opts,
            theme=theme
        )


@pd.api.extensions.register_series_accessor("echart")
class SeriesEcharts:
    def __init__(self, series_obj):
        self._obj = series_obj

    def _get_dist(self, dtype, bins):
        df = self._obj.copy().to_frame()
        xcol = df.columns[0]

        if dtype is None:
            dtype = infer_dtype(df[xcol])
        if dtype == "value":
            # TODO: 当数据本身不超过max_bins的大小还需要调用这个函数
            df[xcol] = _categorize_array(df[xcol].values.tolist(), bins=bins)
            df = df.sort_values(by=xcol)

        ycol = "count_" if xcol == "count" else "count"
        df[ycol] = 1
        return df, xcol, ycol

    def pie(self,
            xtype=None,
            bins=None,
            title="",
            subtitle="",
            label_show=False,
            label_opts={},
            legend_opts={},
            theme=None):
        df, xcol, ycol = self._get_dist(xtype, bins)
        return get_pie(
            df,
            xcol,
            ycol,
            title=title,
            subtitle=subtitle,
            label_show=label_show,
            label_opts=label_opts,
            agg_func='sum',
            legend_opts=legend_opts,
            theme=theme,
        )

    def bar(self,
            xtype=None,
            bins=None,
            xaxis_name=None,
            yaxis_name="count",
            title="",
            subtitle="",
            reverse_axis=False,
            label_show=False,
            label_opts={},
            legend_opts={},
            theme=None):
        df, xcol, ycol = self._get_dist(xtype, bins)
        if xaxis_name is None:
            xaxis_name = str(xcol)
        return get_bar(
            df,
            xcol,
            [ycol],
            xaxis_name=xaxis_name,
            yaxis_name=yaxis_name,
            title=title,
            subtitle=subtitle,
            label_show=label_show,
            label_opts=label_opts,
            agg_func='sum',
            stack_view=False,
            reverse_axis=reverse_axis,
            legend_opts=legend_opts,
            theme=theme,
        )

    def line(self,
             xtype=None,
             bins=None,
             xaxis_name=None,
             yaxis_name="count",
             title=None,
             subtitle=None,
             smooth=False,
             label_show=False,
             label_opts={},
             legend_opts={},
             theme=None):
        df, xcol, ycol = self._get_dist(xtype, bins)
        if xaxis_name is None:
            xaxis_name = str(xcol)
        return get_line(
            df,
            xcol,
            [ycol],
            xtype=xtype,
            xaxis_name=xaxis_name,
            yaxis_name=yaxis_name,
            title=title,
            subtitle=subtitle,
            agg_func="sum",
            smooth=smooth,
            label_show=label_show,
            label_opts=label_opts,
            legend_opts=legend_opts,
            theme=theme
        )

    def boxplot(self,
                xaxis_name=None,
                yaxis_name="",
                title="",
                subtitle="",
                legend_opts={},
                theme=None):
        df = self._obj.to_frame()
        xcol = df.columns[0]
        if xaxis_name is None:
            xaxis_name = str(xcol)
        return get_boxplot(
                df,
                [xcol],
                xaxis_name=xaxis_name,
                yaxis_name=yaxis_name,
                title=title,
                subtitle=subtitle,
                legend_opts=legend_opts,
                theme=theme
        )

    def geo(self,
            maptype,
            title="",
            subtitle="",
            label_show=False,
            visualmap=False,
            visualmap_opts={},
            theme=None):
        df, xcol, ycol = self._get_dist('category', None)
        return get_geo(
            df,
            xcol,
            [ycol],
            maptype=maptype,
            title=title,
            subtitle=subtitle,
            agg_func='sum',
            label_show=label_show,
            visualmap=visualmap,
            visualmap_opts=visualmap_opts,
            theme=theme
        )

    def map(self,
            maptype,
            title="",
            subtitle="",
            label_show=False,
            visualmap=False,
            visualmap_opts={},
            theme=None):
        df, xcol, ycol = self._get_dist('category', None)
        return get_map(
            df,
            xcol,
            ycol,
            maptype=maptype,
            title=title,
            subtitle=subtitle,
            agg_func='sum',
            label_show=label_show,
            visualmap=visualmap,
            visualmap_opts=visualmap_opts,
            theme=theme
        )
