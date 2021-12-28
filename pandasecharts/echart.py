import warnings
import pandas as pd
from .core.chart_tool import get_pie, get_bar, get_line, get_scatter
from .core.chart_tool import get_bar3d, get_line3d, get_scatter3d
from .core.chart_tool import get_boxplot, get_funnel, get_geo, get_map
from .core.chart_tool import timeline_decorator, by_decorator
from .core.data_tool import infer_dtype, _categorize_array
from .configs.chart_cfg import PieConfig, BarConfig, LineConfig, ScatterConfig
from .configs.chart_cfg import Bar3DConfig, Line3DConfig, Scatter3DConfig
from .configs.chart_cfg import BoxplotConfig, FunnelConfig, GeoConfig
from .configs.chart_cfg import MapConfig


@pd.api.extensions.register_dataframe_accessor("echart")
class DataFrameEcharts:
    def __init__(self, pandas_obj):
        self._obj = pandas_obj

    # TODO: datazoom? datazoom_opts?
    # TODO: 有没有可能by在timeline后面，即先timeiline，后by
    def pie(self,
            x,
            y,
            title="",
            subtitle="",
            agg_func=None,
            label_show=True,
            figsize=None,
            theme=None,
            center=None,
            radius=None,
            rosetype=None,
            by=None,
            timeline=None,
            init_opts=None,
            label_opts=None,
            title_opts=None,
            legend_opts=None,
            pie_opts=None,
            timeline_opts=None):
        """pie chart

        Args:
        ----
            x (int or str): pandas column name for x axis
            y (int or str): pandas column name for y axis
            title (str, optional): Defaults to "".
                chart's title to show.
            subtitle (str, optional): Defaults to "".
                chart's subtitle to show.
            agg_func (str, optional): Defaults to None.
                aggerate function name, e.g. "mean" "sum".
                equals to df.groupby(x)[y].agg(agg_func).
            label_show (bool, optional): Defaults to False.
                show labels for chart.
            figsize (tuple, optional): Defaults to None.
                a tuple of chart's (width, height).
            theme (str, optional): Defaults to None. chart's theme.
            by (str, optional): Defaults to None.
                pandas column name for separate groups.
            timeline (str, optional): Defaults to None.
                pandas column name for timeline.
            init_opts (dict, optional): Default to None.
                same as pyecharts init_opts.
            label_opts (dict, optional): Defaults to None.
                same as pyecharts label_opts.
            title_opts (dict, optional): Defaults to None.
                same as pyecharts title_opts.
            legend_opts (dict, optional): Defaults to None.
                same as pyecharts legend_opts.
            timeline_opts (dict, optional): Defaults to None.
                used like pyecharts timeline.add_schema(**timeline_opts).

        Returns:
        ---
            pyecharts.charts.basic_charts.pie.Pie: pie chart
        """
        df = self._obj.copy()
        df[x] = df[x].astype(str)

        pie_cfg = PieConfig()
        init_opts = pie_cfg.get_init_opts(init_opts, theme, figsize)
        label_opts = pie_cfg.get_label_opts(label_opts, label_show)
        title_opts = pie_cfg.get_title_opts(title_opts, title, subtitle)
        legend_opts = pie_cfg.get_legend_opts(legend_opts)
        pie_opts = pie_cfg.get_pie_opts(pie_opts, center, radius, rosetype)

        td = timeline_decorator(timeline, timeline_opts, init_opts)
        bd = by_decorator(by=by)
        return td(bd(get_pie))(
            df=df,
            x=x,
            y=y,
            agg_func=agg_func,
            init_opts=init_opts,
            label_opts=label_opts,
            title_opts=title_opts,
            legend_opts=legend_opts,
            pie_opts=pie_opts
        )

    def bar(self,
            x,
            ys,
            xaxis_name=None,
            yaxis_names="",
            title="",
            subtitle="",
            sort=None,
            agg_func=None,
            multiple_yaxis=False,
            stack_view=False,
            label_show=False,
            reverse_axis=False,
            figsize=None,
            theme=None,
            by=None,
            timeline=None,
            init_opts=None,
            label_opts=None,
            title_opts=None,
            legend_opts=None,
            timeline_opts=None,
            xaxis_opts=None,
            yaxis_opts=None,
            tooltip_opts=None):
        """bar chart

        Args:
            x (int or str): pandas column name for x axis
            ys (int or str): pandas column name for multiple y axis
            xaxis_name (str, optional): Defaults to None.
                xais name to show, If None, same as x.
            yaxis_name (str, optional): yaxis name to show. Defaults to "".
            title (str, optional): chart's title to show. Defaults to "".
            subtitle (str, optional): chart's subtitle to show. Defaults to "".
            sort ([type], optional): [description]. Defaults to None.
            agg_func ([type], optional): [description]. Defaults to None.
            stack_view (bool, optional): [description]. Defaults to False.
            label_show (bool, optional): [description]. Defaults to False.
            label_opts (dict, optional): [description]. Defaults to None.
            reverse_axis (bool, optional): [description]. Defaults to False.
            legend_opts (dict, optional): [description]. Defaults to None.
            figsize ([type], optional): [description]. Defaults to None.
            theme ([type], optional): [description]. Defaults to None.
            by ([type], optional): [description]. Defaults to None.
            timeline ([type], optional): [description]. Defaults to None.
            timeline_opts (dict, optional): [description]. Defaults to None.

        Returns:
            [type]: [description]
        """
        df = self._obj.copy()
        # 由于dataframe的bar的x轴可以只考虑离散值，所以先按照
        # x排序，然后将x转为字符串类型，注意要在转str前排序，要不然
        # 会按照字典排序，从而造成数字排序很奇怪
        df = df.sort_values(by=x)
        df[x] = df[x].astype(str)

        if xaxis_name is None:
            xaxis_name = str(x)

        if not isinstance(yaxis_names, list):
            yaxis_names = [yaxis_names]*len(ys)

        if not isinstance(ys, list):
            ys = [ys]

        bar_cfg = BarConfig()
        init_opts = bar_cfg.get_init_opts(init_opts, theme, figsize)
        label_opts = bar_cfg.get_label_opts(label_opts, label_show,
                                            stack_view or reverse_axis)
        title_opts = bar_cfg.get_title_opts(title_opts, title, subtitle)
        legend_opts = bar_cfg.get_legend_opts(legend_opts)
        xaxis_opts = bar_cfg.get_xaxis_opts(xaxis_opts, xaxis_name,
                                            multiple_yaxis)
        yaxis_opts = bar_cfg.get_yaxis_opts(yaxis_opts, yaxis_names[0])
        tooltip_opts = bar_cfg.get_tooltip_opts(tooltip_opts, multiple_yaxis)

        td = timeline_decorator(timeline, timeline_opts, init_opts)
        bd = by_decorator(by=by)
        return td(bd(get_bar))(
            df=df,
            x=x,
            ys=ys,
            yaxis_names=yaxis_names,
            sort=sort,
            agg_func=agg_func,
            multiple_yaxis=multiple_yaxis,
            stack_view=stack_view,
            reverse_axis=reverse_axis,
            init_opts=init_opts,
            label_opts=label_opts,
            title_opts=title_opts,
            legend_opts=legend_opts,
            xaxis_opts=xaxis_opts,
            yaxis_opts=yaxis_opts,
            tooltip_opts=tooltip_opts
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
              figsize=None,
              theme=None,
              by=None,
              init_opts=None,
              title_opts=None,
              visualmap_opts=None,
              xaxis_opts=None,
              yaxis_opts=None,
              zaxis_opts=None):
        df = self._obj.copy()

        if xaxis_name is None:
            xaxis_name = str(x)
        if yaxis_name is None:
            yaxis_name = str(y)
        if zaxis_name is None:
            zaxis_name = str(z)

        bar3d_cfg = Bar3DConfig()
        init_opts = bar3d_cfg.get_init_opts(init_opts, theme, figsize)
        title_opts = bar3d_cfg.get_title_opts(title_opts, title, subtitle)
        xaxis_opts = bar3d_cfg.get_xaxis_opts(xaxis_opts, xaxis_name)
        yaxis_opts = bar3d_cfg.get_yaxis_opts(yaxis_opts, yaxis_name)
        zaxis_opts = bar3d_cfg.get_zaxis_opts(zaxis_opts, zaxis_name)
        visualmap_opts = bar3d_cfg.get_visualmap_opts(visualmap_opts)

        bd = by_decorator(by=by)
        return bd(get_bar3d)(
            df=df,
            x=x,
            y=y,
            z=z,
            visualmap=visualmap,
            init_opts=init_opts,
            title_opts=title_opts,
            xaxis_opts=xaxis_opts,
            yaxis_opts=yaxis_opts,
            zaxis_opts=zaxis_opts,
            visualmap_opts=visualmap_opts,
        )

    def line(self,
             x,
             ys,
             xtype=None,
             xaxis_name=None,
             yaxis_names="",
             title="",
             subtitle="",
             agg_func=None,
             smooth=False,
             multiple_yaxis=False,
             label_show=False,
             figsize=None,
             theme=None,
             by=None,
             timeline=None,
             init_opts=None,
             label_opts=None,
             title_opts=None,
             legend_opts=None,
             xaxis_opts=None,
             yaxis_opts=None,
             tooltip_opts=None,
             timeline_opts=None):
        df = self._obj.copy()
        if xaxis_name is None:
            xaxis_name = x

        if not isinstance(yaxis_names, list):
            yaxis_names = [yaxis_names]*len(ys)

        if not isinstance(ys, list):
            ys = [ys]

        if xtype is None:
            xtype = infer_dtype(df[x])
            warnings.warn("Please specify argument xtype,"
                          f" \'{xtype}\' is infered!")

        if xtype == "category":
            df[x] = df[x].astype(str)

        line_cfg = LineConfig()
        init_opts = line_cfg.get_init_opts(init_opts, theme, figsize)
        label_opts = line_cfg.get_label_opts(label_opts, label_show)
        title_opts = line_cfg.get_title_opts(title_opts, title, subtitle)
        legend_opts = line_cfg.get_legend_opts(legend_opts)
        xaxis_opts = line_cfg.get_xaxis_opts(xaxis_opts, xaxis_name, xtype)
        yaxis_opts = line_cfg.get_yaxis_opts(yaxis_opts, yaxis_names[0])
        tooltip_opts = line_cfg.get_tooltip_opts(tooltip_opts, multiple_yaxis)

        td = timeline_decorator(timeline, timeline_opts, init_opts)
        bd = by_decorator(by=by)
        return td(bd(get_line))(
            df=df,
            x=x,
            ys=ys,
            yaxis_names=yaxis_names,
            agg_func=agg_func,
            smooth=smooth,
            multiple_yaxis=multiple_yaxis,
            init_opts=init_opts,
            label_opts=label_opts,
            title_opts=title_opts,
            legend_opts=legend_opts,
            xaxis_opts=xaxis_opts,
            yaxis_opts=yaxis_opts,
            tooltip_opts=tooltip_opts
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
               figsize=None,
               theme=None,
               by=None,
               init_opts=None,
               title_opts=None,
               xaxis_opts=None,
               yaxis_opts=None,
               zaxis_opts=None,
               visualmap_opts=None):
        df = self._obj.copy()
        if xaxis_name is None:
            xaxis_name = str(x)
        if yaxis_name is None:
            yaxis_name = str(y)
        if zaxis_name is None:
            zaxis_name = str(z)

        if xtype is None:
            xtype = infer_dtype(df[x])
            warnings.warn("Please specify argument xtype,"
                          f" \'{xtype}\' is infered!")
        if ytype is None:
            ytype = infer_dtype(df[y])
            warnings.warn("Please specify argument ytype"
                          f", \'{ytype}\' is infered!")
        if ztype is None:
            ztype = infer_dtype(df[z])
            warnings.warn(f"Please specify argument ztype,"
                          f" \'{ztype}\' is infered!")

        line3d_cfg = Line3DConfig()
        init_opts = line3d_cfg.get_init_opts(init_opts, theme, figsize)
        title_opts = line3d_cfg.get_title_opts(title_opts, title, subtitle)
        xaxis_opts = line3d_cfg.get_xaxis_opts(xaxis_opts, xaxis_name, xtype)
        yaxis_opts = line3d_cfg.get_yaxis_opts(yaxis_opts, yaxis_name, ytype)
        zaxis_opts = line3d_cfg.get_zaxis_opts(zaxis_opts, zaxis_name, ztype)
        visualmap_opts = line3d_cfg.get_visualmap_opts(visualmap_opts)

        bd = by_decorator(by=by)
        return bd(get_line3d)(
            df=df,
            x=x,
            y=y,
            z=z,
            visualmap=visualmap,
            init_opts=init_opts,
            title_opts=title_opts,
            xaxis_opts=xaxis_opts,
            yaxis_opts=yaxis_opts,
            zaxis_opts=zaxis_opts,
            visualmap_opts=visualmap_opts
        )

    def scatter(self,
                x,
                ys,
                xtype=None,
                xaxis_name=None,
                yaxis_names="",
                title="",
                subtitle="",
                agg_func=None,
                multiple_yaxis=False,
                label_show=False,
                visualmap=False,
                figsize=None,
                theme=None,
                by=None,
                timeline=None,
                init_opts=None,
                label_opts=None,
                title_opts=None,
                legend_opts=None,
                xaxis_opts=None,
                yaxis_opts=None,
                timeline_opts=None,
                visualmap_opts=None):
        df = self._obj.copy()
        df[x] = df[x].astype(str)

        if xaxis_name is None:
            xaxis_name = x

        if not isinstance(yaxis_names, list):
            yaxis_names = [yaxis_names]*len(ys)

        if not isinstance(ys, list):
            ys = [ys]

        if xtype is None:
            xtype = infer_dtype(df[x])
            warnings.warn("Please specify argument xtype,"
                          f" \'{xtype}\' is infered!")

        scatter_cfg = ScatterConfig()
        init_opts = scatter_cfg.get_init_opts(init_opts, theme, figsize)
        label_opts = scatter_cfg.get_label_opts(label_opts, label_show)
        title_opts = scatter_cfg.get_title_opts(title_opts, title, subtitle)
        legend_opts = scatter_cfg.get_legend_opts(legend_opts)
        xaxis_opts = scatter_cfg.get_xaxis_opts(xaxis_opts, xaxis_name, xtype)
        yaxis_opts = scatter_cfg.get_yaxis_opts(yaxis_opts, yaxis_names[0])
        visualmap_opts = scatter_cfg.get_visualmap_opts(visualmap_opts)

        td = timeline_decorator(timeline, timeline_opts, init_opts)
        bd = by_decorator(by=by)
        return td(bd(get_scatter))(
            df=df,
            x=x,
            ys=ys,
            yaxis_names=yaxis_names,
            agg_func=agg_func,
            multiple_yaxis=multiple_yaxis,
            visualmap=visualmap,
            init_opts=init_opts,
            label_opts=label_opts,
            title_opts=title_opts,
            legend_opts=legend_opts,
            xaxis_opts=xaxis_opts,
            yaxis_opts=yaxis_opts,
            visualmap_opts=visualmap_opts
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
                  figsize=None,
                  theme=None,
                  by=None,
                  init_opts=None,
                  title_opts=None,
                  xaxis_opts=None,
                  yaxis_opts=None,
                  zaxis_opts=None,
                  visualmap_opts=None):
        df = self._obj.copy()
        if xaxis_name is None:
            xaxis_name = str(x)
        if yaxis_name is None:
            yaxis_name = str(y)
        if zaxis_name is None:
            zaxis_name = str(z)

        if xtype is None:
            xtype = infer_dtype(df[x])
            warnings.warn("Please specify argument xtype,"
                          f" \'{xtype}\' is infered!")
        if ytype is None:
            ytype = infer_dtype(df[y])
            warnings.warn("Please specify argument ytype,"
                          f" \'{ytype}\' is infered!")
        if ztype is None:
            ztype = infer_dtype(df[z])
            warnings.warn(f"Please specify argument ztype,"
                          f" \'{ztype}\' is infered!")

        scatter3d_cfg = Scatter3DConfig()
        init_opts = scatter3d_cfg.get_init_opts(init_opts, theme, figsize)
        title_opts = scatter3d_cfg.get_title_opts(title_opts, title, subtitle)
        xaxis_opts = scatter3d_cfg.get_xaxis_opts(xaxis_opts,
                                                  xaxis_name,
                                                  xtype)
        yaxis_opts = scatter3d_cfg.get_yaxis_opts(yaxis_opts,
                                                  yaxis_name,
                                                  ytype)
        zaxis_opts = scatter3d_cfg.get_zaxis_opts(zaxis_opts,
                                                  zaxis_name,
                                                  ztype)
        visualmap_opts = scatter3d_cfg.get_visualmap_opts(visualmap_opts)

        bd = by_decorator(by=by)
        return bd(get_scatter3d)(
            df=df,
            x=x,
            y=y,
            z=z,
            visualmap=visualmap,
            init_opts=init_opts,
            title_opts=title_opts,
            xaxis_opts=xaxis_opts,
            yaxis_opts=yaxis_opts,
            zaxis_opts=zaxis_opts,
            visualmap_opts=visualmap_opts
        )

    def boxplot(self,
                ys,
                xaxis_name="",
                yaxis_name="",
                title="",
                subtitle="",
                figsize=None,
                theme=None,
                by=None,
                timeline=None,
                init_opts=None,
                title_opts=None,
                legend_opts=None,
                xaxis_opts=None,
                yaxis_opts=None,
                timeline_opts=None):
        df = self._obj.copy()

        if not isinstance(ys, list):
            ys = [ys]

        boxplot_cfg = BoxplotConfig()
        init_opts = boxplot_cfg.get_init_opts(init_opts, theme, figsize)
        title_opts = boxplot_cfg.get_title_opts(title_opts, title, subtitle)
        legend_opts = boxplot_cfg.get_legend_opts(legend_opts)
        xaxis_opts = boxplot_cfg.get_xaxis_opts(xaxis_opts, xaxis_name)
        yaxis_opts = boxplot_cfg.get_yaxis_opts(yaxis_opts, yaxis_name)

        td = timeline_decorator(timeline, timeline_opts, init_opts)
        bd = by_decorator(by=by)
        return td(bd(get_boxplot))(
            df=df,
            ys=ys,
            init_opts=init_opts,
            title_opts=title_opts,
            legend_opts=legend_opts,
            xaxis_opts=xaxis_opts,
            yaxis_opts=yaxis_opts,
        )

    def funnel(self,
               x,
               y,
               title="",
               subtitle="",
               ascending=False,
               label_show=True,
               position="inner",
               figsize=None,
               theme=None,
               by=None,
               timeline=None,
               init_opts=None,
               label_opts=None,
               title_opts=None,
               legend_opts=None,
               timeline_opts=None):
        df = self._obj.copy()
        funnel_cfg = FunnelConfig()
        init_opts = funnel_cfg.get_init_opts(init_opts, theme, figsize)
        title_opts = funnel_cfg.get_title_opts(title_opts, title, subtitle)
        label_opts = funnel_cfg.get_label_opts(label_opts, label_show,
                                               position)
        legend_opts = funnel_cfg.get_legend_opts(legend_opts)
        td = timeline_decorator(timeline, timeline_opts, init_opts)
        bd = by_decorator(by=by)
        return td(bd(get_funnel))(
            df=df,
            x=x,
            y=y,
            ascending=ascending,
            init_opts=init_opts,
            label_opts=label_opts,
            title_opts=title_opts,
            legend_opts=legend_opts,
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
            figsize=None,
            theme=None,
            by=None,
            timeline=None,
            init_opts=None,
            label_opts=None,
            title_opts=None,
            visualmap_opts=None,
            timeline_opts=None):
        df = self._obj.copy()
        if not isinstance(ys, list):
            ys = [ys]

        geo_cfg = GeoConfig()
        init_opts = geo_cfg.get_init_opts(init_opts, theme, figsize)
        label_opts = geo_cfg.get_label_opts(label_opts, label_show)
        title_opts = geo_cfg.get_title_opts(title_opts, title, subtitle)
        visualmap_opts = geo_cfg.get_visualmap_opts(visualmap_opts)

        td = timeline_decorator(timeline, timeline_opts, init_opts)
        bd = by_decorator(by=by)
        return td(bd(get_geo))(
            df=df,
            x=x,
            ys=ys,
            maptype=maptype,
            agg_func=agg_func,
            visualmap=visualmap,
            init_opts=init_opts,
            label_opts=label_opts,
            title_opts=title_opts,
            visualmap_opts=visualmap_opts
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
            figsize=None,
            theme=None,
            by=None,
            timeline=None,
            init_opts=None,
            label_opts=None,
            title_opts=None,
            visualmap_opts=None,
            timeline_opts=None):
        df = self._obj.copy()

        map_cfg = MapConfig()
        init_opts = map_cfg.get_init_opts(init_opts, theme, figsize)
        label_opts = map_cfg.get_label_opts(label_opts, label_show)
        title_opts = map_cfg.get_title_opts(title_opts, title, subtitle)
        visualmap_opts = map_cfg.get_visualmap_opts(visualmap_opts)

        td = timeline_decorator(timeline, timeline_opts, init_opts)
        bd = by_decorator(by=by)
        return td(bd(get_map))(
            df=df,
            x=x,
            y=y,
            maptype=maptype,
            agg_func=agg_func,
            visualmap=visualmap,
            init_opts=init_opts,
            label_opts=label_opts,
            title_opts=title_opts,
            visualmap_opts=visualmap_opts,
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
            df[xcol] = _categorize_array(df[xcol].values.tolist(), bins=bins)
            df = df.sort_values(by=xcol)

        ycol = "count_" if xcol == "count" else "count"
        df[ycol] = 1
        return df, xcol, ycol, dtype

    def pie(self,
            xtype=None,
            bins=None,
            title="",
            subtitle="",
            label_show=True,
            figsize=None,
            theme=None,
            init_opts=None,
            label_opts=None,
            title_opts=None,
            legend_opts=None):
        # TODO: 是否加个fillna=None，如果是None表示dropna，如果是int则填充，如果是字符串则用方法填充？
        pie_cfg = PieConfig()
        init_opts = pie_cfg.get_init_opts(init_opts, theme, figsize)
        label_opts = pie_cfg.get_label_opts(label_opts, label_show)
        title_opts = pie_cfg.get_title_opts(title_opts, title, subtitle)
        legend_opts = pie_cfg.get_legend_opts(legend_opts)

        df, xcol, ycol, xtype = self._get_dist(xtype, bins)
        return get_pie(
            df,
            xcol,
            ycol,
            agg_func='sum',
            init_opts=init_opts,
            label_opts=label_opts,
            title_opts=title_opts,
            legend_opts=legend_opts
        )

    def bar(self,
            xtype=None,
            bins=None,
            xaxis_name=None,
            yaxis_name="count",
            title="",
            subtitle="",
            sort=None,
            reverse_axis=False,
            label_show=False,
            figsize=None,
            theme=None,
            init_opts=None,
            label_opts=None,
            title_opts=None,
            legend_opts=None,
            xaxis_opts=None,
            yaxis_opts=None):
        df, xcol, ycol, xtype = self._get_dist(xtype, bins)
        if xaxis_name is None:
            xaxis_name = str(xcol)
        if sort is not None:
            sort = ycol

        bar_cfg = BarConfig()
        init_opts = bar_cfg.get_init_opts(init_opts, theme, figsize)
        label_opts = bar_cfg.get_label_opts(label_opts, label_show,
                                            position=reverse_axis)
        title_opts = bar_cfg.get_title_opts(title_opts, title, subtitle)
        legend_opts = bar_cfg.get_legend_opts(legend_opts)
        xaxis_opts = bar_cfg.get_xaxis_opts(xaxis_opts, xaxis_name)
        yaxis_opts = bar_cfg.get_yaxis_opts(yaxis_opts, yaxis_name)

        return get_bar(
            df,
            xcol,
            [ycol],
            yaxis_names=[yaxis_name],
            sort=sort,
            agg_func='sum',
            multiple_yaxis=False,
            stack_view=False,
            reverse_axis=reverse_axis,
            init_opts=init_opts,
            label_opts=label_opts,
            title_opts=title_opts,
            legend_opts=legend_opts,
            xaxis_opts=xaxis_opts,
            yaxis_opts=yaxis_opts
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
             figsize=None,
             theme=None,
             init_opts=None,
             label_opts=None,
             title_opts=None,
             legend_opts=None,
             xaxis_opts=None,
             yaxis_opts=None,
             tooltip_opts=None):
        df, xcol, ycol, xtype = self._get_dist(xtype, bins)
        if xaxis_name is None:
            xaxis_name = str(xcol)

        line_cfg = LineConfig()
        init_opts = line_cfg.get_init_opts(init_opts, theme, figsize)
        label_opts = line_cfg.get_label_opts(label_opts, label_show)
        title_opts = line_cfg.get_title_opts(title_opts, title, subtitle)
        legend_opts = line_cfg.get_legend_opts(legend_opts)
        xaxis_opts = line_cfg.get_xaxis_opts(xaxis_opts, xaxis_name, xtype)
        yaxis_opts = line_cfg.get_yaxis_opts(yaxis_opts, yaxis_name)
        tooltip_opts = line_cfg.get_tooltip_opts(tooltip_opts)

        return get_line(
            df,
            xcol,
            [ycol],
            multiple_yaxis=False,
            yaxis_names=[yaxis_name],
            agg_func="sum",
            smooth=smooth,
            init_opts=init_opts,
            label_opts=label_opts,
            title_opts=title_opts,
            legend_opts=legend_opts,
            xaxis_opts=xaxis_opts,
            yaxis_opts=yaxis_opts,
            tooltip_opts=tooltip_opts
        )

    def boxplot(self,
                xaxis_name=None,
                yaxis_name="",
                title="",
                subtitle="",
                figsize=None,
                theme=None,
                init_opts=None,
                title_opts=None,
                legend_opts=None,
                xaxis_opts=None,
                yaxis_opts=None):
        df = self._obj.to_frame()
        xcol = df.columns[0]
        if xaxis_name is None:
            xaxis_name = str(xcol)
        boxplot_cfg = BoxplotConfig()
        init_opts = boxplot_cfg.get_init_opts(init_opts, theme, figsize)
        title_opts = boxplot_cfg.get_title_opts(title_opts, title, subtitle)
        xaxis_opts = boxplot_cfg.get_xaxis_opts(xaxis_opts, xaxis_name)
        yaxis_opts = boxplot_cfg.get_yaxis_opts(yaxis_opts, yaxis_name)
        return get_boxplot(
            df,
            [xcol],
            init_opts=init_opts,
            title_opts=title_opts,
            legend_opts=legend_opts,
            xaxis_opts=xaxis_opts,
            yaxis_opts=yaxis_opts,
        )

    def geo(self,
            maptype,
            title="",
            subtitle="",
            label_show=False,
            visualmap=False,
            figsize=None,
            theme=None,
            init_opts=None,
            label_opts=None,
            title_opts=None,
            visualmap_opts=None):
        df, xcol, ycol, xtype = self._get_dist('category', None)
        geo_cfg = GeoConfig()
        init_opts = geo_cfg.get_init_opts(init_opts, theme, figsize)
        label_opts = geo_cfg.get_label_opts(label_opts, label_show)
        title_opts = geo_cfg.get_title_opts(title_opts, title, subtitle)

        return get_geo(
            df,
            xcol,
            [ycol],
            maptype=maptype,
            agg_func='sum',
            visualmap=visualmap,
            init_opts=init_opts,
            label_opts=label_opts,
            title_opts=title_opts,
            visualmap_opts=visualmap_opts
        )

    def map(self,
            maptype,
            title="",
            subtitle="",
            label_show=False,
            visualmap=False,
            figsize=None,
            theme=None,
            init_opts=None,
            label_opts=None,
            title_opts=None,
            visualmap_opts=None):
        df, xcol, ycol, xtype = self._get_dist('category', None)

        map_cfg = MapConfig()
        init_opts = map_cfg.get_init_opts(init_opts, theme, figsize)
        label_opts = map_cfg.get_label_opts(label_opts, label_show)
        title_opts = map_cfg.get_title_opts(title_opts, title, subtitle)
        return get_map(
            df,
            xcol,
            ycol,
            maptype=maptype,
            agg_func='sum',
            visualmap=visualmap,
            init_opts=init_opts,
            label_opts=label_opts,
            title_opts=title_opts,
            visualmap_opts=visualmap_opts,
        )
