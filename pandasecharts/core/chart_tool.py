import warnings
import copy
from pyecharts.charts import Page, Timeline
from pyecharts.charts import Line, Bar, Pie, Scatter
from pyecharts.charts import Line3D, Bar3D, Scatter3D
from pyecharts.charts import Boxplot, Funnel, Geo, Map
from pyecharts import options as opts


def by_decorator(by=None):
    def wrapper(func):
        def inner(**kwargs):
            if by is not None:
                page = Page(layout=Page.DraggablePageLayout)
                for by_value, by_df in kwargs["df"].groupby(by):
                    new_kwargs = copy.deepcopy(kwargs)
                    new_kwargs["df"] = by_df
                    new_kwargs["title_opts"]["subtitle"] += f"{by}={by_value}"
                    chart_ = func(**new_kwargs)
                    page.add(chart_)
                return page
            else:
                return func(**kwargs)
        return inner
    return wrapper


def timeline_decorator(timeline=None, timeline_opts=None, init_opts=None):
    if timeline_opts is None:
        timeline_opts = {}

    def wrapper(func):
        def inner(**kwargs):
            if timeline is not None:
                tl = Timeline(init_opts=opts.InitOpts(**init_opts))
                tl.add_schema(**timeline_opts)
                for t, df_ in kwargs["df"].groupby(timeline):
                    new_kwargs = copy.deepcopy(kwargs)
                    new_kwargs["title_opts"]["title"] += f"{timeline}={t}"
                    new_kwargs["df"] = df_
                    chart_ = func(**new_kwargs)
                    tl.add(chart_, f"{t}")
                return tl
            else:
                return func(**kwargs)
        return inner
    return wrapper


def get_pie(df,
            x,
            y,
            agg_func,
            init_opts,
            label_opts,
            title_opts,
            legend_opts,
            pie_opts):
    if agg_func is not None:
        df = df.groupby(x)[y].agg(agg_func).reset_index()

    pie = Pie(init_opts=opts.InitOpts(**init_opts))
    pie = (
        pie
        .add(str(y), df[[x, y]].values.tolist(), **pie_opts)
        .set_series_opts(
            label_opts=opts.LabelOpts(**label_opts)
        )
        .set_global_opts(
            title_opts=opts.TitleOpts(**title_opts),
            legend_opts=opts.LegendOpts(**legend_opts),
        )
    )
    return pie


def get_bar(df,
            x,
            ys,
            yaxis_names,
            sort,
            agg_func,
            multiple_yaxis,
            stack_view,
            reverse_axis,
            init_opts,
            label_opts,
            title_opts,
            legend_opts,
            xaxis_opts,
            yaxis_opts,
            tooltip_opts):
    if stack_view:
        stack = ["1"]*len(ys)
    else:
        stack = [str(i) for i in range(1, len(ys)+1)]

    if agg_func is not None:
        df = df.groupby(x)[ys].agg(agg_func).reset_index()

    if sort is not None:
        # 排序显示的顺序和是否反转坐标轴有关
        df = df.sort_values(by=sort, ascending=reverse_axis)

    bar = Bar(init_opts=opts.InitOpts(**init_opts))
    bar = bar.add_xaxis(df[x].values.tolist())
    if multiple_yaxis:
        for i, y in enumerate(ys):
            bar.add_yaxis(str(y),
                          df[y].values.tolist(),
                          yaxis_index=i)
        for j in range(1, len(ys)):
            bar.extend_axis(
                yaxis=opts.AxisOpts(name=yaxis_names[j],
                                    offset=30 * (j-1))
            )
    else:
        for y, st in zip(ys, stack):
            bar.add_yaxis(str(y), df[y].values.tolist(), stack=st)

    bar.set_series_opts(
        label_opts=opts.LabelOpts(**label_opts),
    )
    # bar的x轴只支持category，不支持value
    if reverse_axis:
        bar.reversal_axis()
        bar.set_global_opts(
            xaxis_opts=opts.AxisOpts(**yaxis_opts),
            yaxis_opts=opts.AxisOpts(**xaxis_opts)
        )
    else:
        bar.set_global_opts(
            xaxis_opts=opts.AxisOpts(**xaxis_opts),
            yaxis_opts=opts.AxisOpts(**yaxis_opts)
        )
    bar.set_global_opts(
        title_opts=opts.TitleOpts(**title_opts),
        legend_opts=opts.LegendOpts(**legend_opts),
        tooltip_opts=opts.TooltipOpts(**tooltip_opts)
    )
    return bar


def get_bar3d(df,
              x,
              y,
              z,
              visualmap,
              init_opts,
              title_opts,
              xaxis_opts,
              yaxis_opts,
              zaxis_opts,
              visualmap_opts):
    bar3d = (
        Bar3D(init_opts=opts.InitOpts(**init_opts))
        .add(
            "",
            data=df[[x, y, z]].values.tolist(),
            xaxis3d_opts=opts.Axis3DOpts(**xaxis_opts),
            yaxis3d_opts=opts.Axis3DOpts(**yaxis_opts),
            zaxis3d_opts=opts.Axis3DOpts(**zaxis_opts),
        )
    )

    if visualmap:
        bar3d.set_global_opts(
            title_opts=opts.TitleOpts(),
            visualmap_opts=opts.VisualMapOpts(**visualmap_opts)
        )
    else:
        bar3d.set_global_opts(
            title_opts=opts.TitleOpts(**title_opts),
        )
    return bar3d


def get_line(df,
             x,
             ys,
             yaxis_names,
             multiple_yaxis,
             agg_func,
             smooth,
             init_opts,
             label_opts,
             title_opts,
             legend_opts,
             xaxis_opts,
             yaxis_opts,
             tooltip_opts):
    # TODO: line的itemType
    if agg_func is not None:
        df = df.groupby(x)[ys].agg(agg_func).reset_index()

    line = Line(init_opts=opts.InitOpts(**init_opts))
    line = line.add_xaxis(df[x].values.tolist())

    if multiple_yaxis:
        for i, y in enumerate(ys):
            line.add_yaxis(str(y),
                           df[y].values.tolist(),
                           is_smooth=smooth,
                           yaxis_index=i)
        for j in range(1, len(ys)):
            line.extend_axis(
                yaxis=opts.AxisOpts(name=yaxis_names[j],
                                    offset=30 * (j-1))
            )
    else:
        for y in ys:
            line.add_yaxis(str(y),
                           df[y].values.tolist(),
                           is_smooth=smooth)

    line.set_series_opts(
        label_opts=opts.LabelOpts(**label_opts)
    )

    line.set_global_opts(
        xaxis_opts=opts.AxisOpts(**xaxis_opts),
        yaxis_opts=opts.AxisOpts(**yaxis_opts),
        title_opts=opts.TitleOpts(**title_opts),
        legend_opts=opts.LegendOpts(**legend_opts),
        tooltip_opts=opts.TooltipOpts(**tooltip_opts),
    )
    return line


def get_line3d(df,
               x,
               y,
               z,
               visualmap,
               init_opts,
               title_opts,
               xaxis_opts,
               yaxis_opts,
               zaxis_opts,
               visualmap_opts):
    line3d = (
        Line3D(init_opts=opts.InitOpts(**init_opts))
        .add(
            "",
            data=df[[x, y, z]].values.tolist(),
            xaxis3d_opts=opts.Axis3DOpts(**xaxis_opts),
            yaxis3d_opts=opts.Axis3DOpts(**yaxis_opts),
            zaxis3d_opts=opts.Axis3DOpts(**zaxis_opts),
        )
    )

    if visualmap:
        line3d.set_global_opts(
            title_opts=opts.TitleOpts(**title_opts),
            visualmap_opts=opts.VisualMapOpts(**visualmap_opts)
        )
    else:
        line3d.set_global_opts(
            title_opts=opts.TitleOpts(**title_opts),
        )
    return line3d


def get_scatter(df,
                x,
                ys,
                yaxis_names,
                agg_func,
                multiple_yaxis,
                visualmap,
                init_opts,
                label_opts,
                title_opts,
                legend_opts,
                xaxis_opts,
                yaxis_opts,
                visualmap_opts):
    if agg_func is not None:
        df = df.groupby(x)[ys].agg(agg_func).reset_index()

    scatter = Scatter(init_opts=opts.InitOpts(**init_opts))
    scatter.add_xaxis(df[x].values.tolist())

    if multiple_yaxis:
        for i, y in enumerate(ys):
            scatter.add_yaxis(str(y),
                              df[y].values.tolist(),
                              yaxis_index=i)
        for j in range(1, len(ys)):
            scatter.extend_axis(
                yaxis=opts.AxisOpts(name=yaxis_names[j],
                                    offset=30 * (j-1))
            )
    else:
        for y in ys:
            scatter.add_yaxis(str(y),
                              df[y].values.tolist())

    scatter.set_series_opts(
        label_opts=opts.LabelOpts(**label_opts)
    )

    if visualmap:
        scatter.set_global_opts(
            xaxis_opts=opts.AxisOpts(**xaxis_opts),
            yaxis_opts=opts.AxisOpts(**yaxis_opts),
            title_opts=opts.TitleOpts(**title_opts),
            legend_opts=opts.LegendOpts(**legend_opts),
            visualmap_opts=opts.VisualMapOpts(**visualmap_opts)
        )
    else:
        scatter.set_global_opts(
            xaxis_opts=opts.AxisOpts(**xaxis_opts),
            yaxis_opts=opts.AxisOpts(**yaxis_opts),
            legend_opts=opts.LegendOpts(**legend_opts),
            title_opts=opts.TitleOpts(**title_opts)
        )
    return scatter


def get_scatter3d(df,
                  x,
                  y,
                  z,
                  visualmap,
                  init_opts,
                  title_opts,
                  xaxis_opts,
                  yaxis_opts,
                  zaxis_opts,
                  visualmap_opts):
    scatter3d = Scatter3D(init_opts=opts.InitOpts(**init_opts))
    scatter3d = (
        scatter3d
        .add(
            "",
            data=df[[x, y, z]].values.tolist(),
            xaxis3d_opts=opts.Axis3DOpts(**xaxis_opts),
            yaxis3d_opts=opts.Axis3DOpts(**yaxis_opts),
            zaxis3d_opts=opts.Axis3DOpts(**zaxis_opts),
        )
    )

    if visualmap:
        scatter3d.set_global_opts(
            title_opts=opts.TitleOpts(**title_opts),
            visualmap_opts=opts.VisualMapOpts(**visualmap_opts)
        )
    else:
        scatter3d.set_global_opts(
            title_opts=opts.TitleOpts(**title_opts),
        )
    return scatter3d


def get_boxplot(df,
                ys,
                init_opts,
                title_opts,
                legend_opts,
                xaxis_opts,
                yaxis_opts):
    boxplot = Boxplot(init_opts=opts.InitOpts(**init_opts))

    if all(isinstance(y, str) for y in ys):
        boxplot.add_xaxis(["expr"])
        for y in ys:
            boxplot.add_yaxis(str(y),
                              boxplot.prepare_data([df[y].values.tolist()]))
    elif all(isinstance(y, list) for y in ys):
        boxplot.add_xaxis([f"expr{i}" for i in range(1, len(ys[0])+1)])
        for y in ys:
            boxplot.add_yaxis("_".join(y),
                              boxplot.prepare_data(df[y].values.T.tolist()))
    else:
        raise ValueError(f"ys {ys} has unkonwn format")
    boxplot.set_global_opts(
        xaxis_opts=opts.AxisOpts(**xaxis_opts),
        yaxis_opts=opts.AxisOpts(**yaxis_opts),
        title_opts=opts.TitleOpts(**title_opts),
        legend_opts=opts.LegendOpts(**legend_opts)
    )
    return boxplot


def get_funnel(df,
               x,
               y,
               ascending,
               init_opts,
               title_opts,
               label_opts,
               legend_opts,):
    funnel = (
        Funnel(init_opts=opts.InitOpts(**init_opts))
        .add(str(y),
             df[[x, y]].values.tolist(),
             sort_="ascending" if ascending else "desending",
             label_opts=opts.LabelOpts(**label_opts))
        .set_global_opts(
            title_opts=opts.TitleOpts(**title_opts),
            legend_opts=opts.LegendOpts(**legend_opts)
        )
    )
    return funnel


def get_geo(df,
            x,
            ys,
            maptype,
            agg_func,
            visualmap,
            init_opts,
            label_opts,
            title_opts,
            visualmap_opts):
    if agg_func is not None:
        df = df.groupby(x)[ys].agg(agg_func).reset_index()

    if maptype is None or len(maptype) == 0:
        warnings.warn("Please specify argument maptype, e.g. 'china'")

    geo = Geo(init_opts=opts.InitOpts(**init_opts))
    geo.add_schema(maptype=maptype)
    for y in ys:
        geo.add(str(y), df[[x, y]].values.tolist())

    geo.set_series_opts(label_opts=opts.LabelOpts(**label_opts))
    if visualmap:
        geo.set_global_opts(
                title_opts=opts.TitleOpts(**title_opts),
                visualmap_opts=opts.VisualMapOpts(**visualmap_opts)
            )
    else:
        geo.set_global_opts(
                title_opts=opts.TitleOpts(**title_opts),
            )
    return geo


def get_map(df,
            x,
            y,
            maptype,
            agg_func,
            visualmap,
            init_opts,
            label_opts,
            title_opts,
            visualmap_opts):
    if agg_func is not None:
        df = df.groupby(x)[y].agg(agg_func).reset_index()

    if maptype is None or len(maptype) == 0:
        warnings.warn("Please specify argument maptype, e.g. 'china'")

    map = (
        Map(init_opts=opts.InitOpts(**init_opts))
        .add(str(y), df[[x, y]].values.tolist(), maptype)
        .set_series_opts(label_opts=opts.LabelOpts(**label_opts))
    )

    if visualmap:
        map.set_global_opts(
            title_opts=opts.TitleOpts(**title_opts),
            visualmap_opts=opts.VisualMapOpts(**visualmap_opts)
        )
    else:
        map.set_global_opts(
            title_opts=opts.TitleOpts(**title_opts),
        )
    return map
