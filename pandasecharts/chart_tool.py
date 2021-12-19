import warnings
import numpy as np
from pyecharts.charts import Page, Timeline
from pyecharts.charts import Line, Bar, Pie, Scatter
from pyecharts.charts import Line3D, Bar3D, Scatter3D
from pyecharts.charts import Boxplot, Funnel, Geo, Map
from pyecharts import options as opts
from .data_tool import infer_dtype


def by_decorator(by=None):
    def wrapper(func):
        def inner(**kwargs):
            if by is not None:
                page = Page(layout=Page.DraggablePageLayout)
                for by_value, by_df in kwargs["df"].groupby(by):
                    new_kwargs = dict(kwargs)
                    new_kwargs["df"] = by_df
                    new_kwargs["subtitle"] += f"{by}={by_value}"
                    chart_ = func(**new_kwargs)
                    page.add(chart_)
                return page
            else:
                return func(**kwargs)
        return inner
    return wrapper


def timeline_decorator(timeline=None, timeline_opts={}, init_opts={}):
    def wrapper(func):
        def inner(**kwargs):
            if timeline is not None:
                tl = Timeline(init_opts=opts.InitOpts(**init_opts))
                tl.add_schema(**timeline_opts)
                for t, df_ in kwargs["df"].groupby(timeline):
                    new_kwargs = dict(kwargs)
                    new_kwargs["title"] = f"{t}{new_kwargs['title']}"
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
            title,
            subtitle,
            label_show,
            label_opts,
            agg_func,
            legend_opts,
            init_opts):
    if agg_func is not None:
        df = df.groupby(x)[y].agg(agg_func).reset_index()

    pie = Pie(init_opts=opts.InitOpts(**init_opts))

    label_opts_ = {
        "formatter": "{b}:{d}%",
        "position": "inner",
        "is_show": label_show
    }
    label_opts_.update(label_opts)

    pie = (
        pie
        .add(str(y), df[[x, y]].values.tolist())
        .set_series_opts(
            label_opts=opts.LabelOpts(**label_opts_)
        )
        .set_global_opts(
            title_opts=opts.TitleOpts(title=title, subtitle=subtitle),
            legend_opts=opts.LegendOpts(**legend_opts),
        )
    )
    return pie


def get_bar(df,
            x,
            ys,
            xaxis_name,
            yaxis_name,
            title,
            subtitle,
            sort,
            agg_func,
            stack_view,
            reverse_axis,
            label_show,
            label_opts,
            legend_opts,
            init_opts):
    # TODO: Bar也支持多y坐标轴
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
    for y, st in zip(ys, stack):
        bar.add_yaxis(str(y), df[y].values.tolist(), stack=st)

    label_opts_ = {
        "position": "right" if stack_view or reverse_axis else "top",
        "is_show": label_show
    }
    label_opts_.update(label_opts)

    bar.set_series_opts(
        label_opts=opts.LabelOpts(**label_opts_),
    )
    # bar的x轴只支持category，不支持value
    if reverse_axis:
        bar.reversal_axis()
        bar.set_global_opts(
            xaxis_opts=opts.AxisOpts(name=yaxis_name, type_='value'),
            yaxis_opts=opts.AxisOpts(name=xaxis_name, type_='category')
        )
    else:
        bar.set_global_opts(
            xaxis_opts=opts.AxisOpts(name=xaxis_name, type_='category'),
            yaxis_opts=opts.AxisOpts(name=yaxis_name, type_='value')
        )
    bar.set_global_opts(
        title_opts=opts.TitleOpts(title=title, subtitle=subtitle),
        legend_opts=opts.LegendOpts(**legend_opts),
    )
    return bar


def get_bar3d(df,
              x,
              y,
              z,
              xaxis_name,
              yaxis_name,
              zaxis_name,
              title,
              subtitle,
              visualmap,
              visualmap_opts,
              init_opts):
    bar3d = (
        Bar3D(init_opts=opts.InitOpts(**init_opts))
        .add(
            "",
            data=df[[x, y, z]].values.tolist(),
            xaxis3d_opts=opts.Axis3DOpts(name=xaxis_name, type_="category"),
            yaxis3d_opts=opts.Axis3DOpts(name=yaxis_name, type_="category"),
            zaxis3d_opts=opts.Axis3DOpts(name=zaxis_name, type_="value"),
        )
    )

    if visualmap:
        bar3d.set_global_opts(
            title_opts=opts.TitleOpts(title=title, subtitle=subtitle),
            visualmap_opts=opts.VisualMapOpts(**visualmap_opts)
        )
    else:
        bar3d.set_global_opts(
            title_opts=opts.TitleOpts(title=title, subtitle=subtitle),
        )
    return bar3d


def get_line(df,
             x,
             ys,
             xtype,
             multiple_yaxis,
             xaxis_name,
             yaxis_names,
             title,
             subtitle,
             agg_func,
             smooth,
             label_show,
             label_opts,
             legend_opts,
             init_opts):
    # TODO: line的itemType
    if xtype is None:
        xtype = infer_dtype(df[x])
        warnings.warn(f"Please specify argument xtype, '{xtype}' is infered!")

    if xtype == "category":
        df[x] = df[x].astype(str)

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

    label_opts_ = {"is_show": label_show}
    label_opts_.update(label_opts)
    line.set_series_opts(
        label_opts=opts.LabelOpts(**label_opts_)
    )

    line.set_global_opts(
        xaxis_opts=opts.AxisOpts(name=xaxis_name, type_=xtype),
        yaxis_opts=opts.AxisOpts(name=yaxis_names[0], type_="value"),
        title_opts=opts.TitleOpts(title=title, subtitle=subtitle),
        legend_opts=opts.LegendOpts(**legend_opts),
        # TODO: tooltips_opts 支持自定义？
        tooltip_opts=opts.TooltipOpts(trigger="axis",
                                      axis_pointer_type="cross"),
    )
    return line


def get_line3d(df,
               x,
               y,
               z,
               xtype,
               ytype,
               ztype,
               xaxis_name,
               yaxis_name,
               zaxis_name,
               title,
               subtitle,
               visualmap,
               visualmap_opts,
               init_opts):
    if xtype is None:
        xtype = infer_dtype(df[x])
        warnings.warn(f"Please specify argument xtype, '{xtype}' is infered!")
    if ytype is None:
        ytype = infer_dtype(df[x])
        warnings.warn(f"Please specify argument ytype, '{ytype}' is infered!")
    if ztype is None:
        ztype = infer_dtype(df[x])
        warnings.warn(f"Please specify argument ztype, '{ztype}' is infered!")

    line3d = (
        Line3D(init_opts=opts.InitOpts(**init_opts))
        .add(
            "",
            data=df[[x, y, z]].values.tolist(),
            xaxis3d_opts=opts.Axis3DOpts(name=xaxis_name, type_=xtype),
            yaxis3d_opts=opts.Axis3DOpts(name=yaxis_name, type_=ytype),
            zaxis3d_opts=opts.Axis3DOpts(name=zaxis_name, type_=ztype),
        )
    )

    if visualmap:
        line3d.set_global_opts(
            title_opts=opts.TitleOpts(title=title, subtitle=subtitle),
            visualmap_opts=opts.VisualMapOpts(**visualmap_opts)
        )
    else:
        line3d.set_global_opts(
            title_opts=opts.TitleOpts(title=title, subtitle=subtitle),
        )
    return line3d


def get_scatter(df,
                x,
                ys,
                xtype,
                xaxis_name,
                yaxis_name,
                title,
                subtitle,
                agg_func,
                label_show,
                label_opts,
                legend_opts,
                visualmap,
                visualmap_opts,
                init_opts):
    if agg_func is not None:
        df = df.groupby(x)[ys].agg(agg_func).reset_index()

    scatter = Scatter(init_opts=opts.InitOpts(**init_opts))
    scatter.add_xaxis(df[x].values.tolist())

    for y in ys:
        scatter.add_yaxis(str(y), df[y].values.tolist())

    label_opts_ = {"is_show": label_show}
    label_opts_.update(label_opts)
    scatter.set_series_opts(
        label_opts=opts.LabelOpts(**label_opts_)
    )

    if xtype is None:
        if df[x].values.dtype.type is np.str_:
            xtype = "category"
        else:
            xtype = "value"
        warnings.warn(
            f"Please specify argument xtype, \'{xtype}\' is infered!")

    if visualmap:
        scatter.set_global_opts(
            xaxis_opts=opts.AxisOpts(name=xaxis_name, type_=xtype),
            yaxis_opts=opts.AxisOpts(name=yaxis_name, type_="value"),
            title_opts=opts.TitleOpts(title=title, subtitle=subtitle),
            legend_opts=opts.LegendOpts(**legend_opts),
            visualmap_opts=opts.VisualMapOpts(**visualmap_opts)
        )
    else:
        scatter.set_global_opts(
            xaxis_opts=opts.AxisOpts(name=xaxis_name, type_=xtype),
            yaxis_opts=opts.AxisOpts(name=yaxis_name, type_="value"),
            legend_opts=opts.LegendOpts(**legend_opts),
            title_opts=opts.TitleOpts(title=title, subtitle=subtitle)
        )
    return scatter


def get_scatter3d(df,
                  x,
                  y,
                  z,
                  xtype,
                  ytype,
                  ztype,
                  xaxis_name,
                  yaxis_name,
                  zaxis_name,
                  title,
                  subtitle,
                  visualmap,
                  visualmap_opts,
                  init_opts):
    if xtype is None:
        xtype = infer_dtype(df[x])
        warnings.warn(f"Please specify argument xtype, '{xtype}' is infered!")
    if ytype is None:
        ytype = infer_dtype(df[x])
        warnings.warn(f"Please specify argument ytype, '{ytype}' is infered!")
    if ztype is None:
        ztype = infer_dtype(df[x])
        warnings.warn(f"Please specify argument ztype, '{ztype}' is infered!")

    scatter3d = Scatter3D(init_opts=opts.InitOpts(**init_opts))
    scatter3d = (
        scatter3d
        .add(
            "",
            data=df[[x, y, z]].values.tolist(),
            xaxis3d_opts=opts.Axis3DOpts(name=xaxis_name, type_=xtype),
            yaxis3d_opts=opts.Axis3DOpts(name=yaxis_name, type_=ytype),
            zaxis3d_opts=opts.Axis3DOpts(name=zaxis_name, type_=ztype),
        )
    )

    if visualmap:
        scatter3d.set_global_opts(
            title_opts=opts.TitleOpts(title=title, subtitle=subtitle),
            visualmap_opts=opts.VisualMapOpts(**visualmap_opts)
        )
    else:
        scatter3d.set_global_opts(
            title_opts=opts.TitleOpts(title=title, subtitle=subtitle),
        )
    return scatter3d


def get_boxplot(df,
                ys,
                xaxis_name,
                yaxis_name,
                title,
                subtitle,
                legend_opts,
                init_opts):
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
        xaxis_opts=opts.AxisOpts(name=xaxis_name),
        yaxis_opts=opts.AxisOpts(name=yaxis_name),
        title_opts=opts.TitleOpts(title=title, subtitle=subtitle),
        legend_opts=opts.LegendOpts(**legend_opts)
    )
    return boxplot


def get_funnel(df,
               x,
               y,
               title,
               subtitle,
               ascending,
               position,
               legend_opts,
               init_opts):
    funnel = (
        Funnel(init_opts=opts.InitOpts(**init_opts))
        .add(str(y),
             df[[x, y]].values.tolist(),
             sort_="ascending" if ascending else "desending",
             label_opts=opts.LabelOpts(position=position))
        .set_global_opts(
            title_opts=opts.TitleOpts(title=title, subtitle=subtitle),
            legend_opts=opts.LegendOpts(**legend_opts)
        )
    )
    return funnel


def get_geo(df,
            x,
            ys,
            maptype,
            title,
            subtitle,
            agg_func,
            label_show,
            visualmap,
            visualmap_opts,
            init_opts):
    if agg_func is not None:
        df = df.groupby(x)[ys].agg(agg_func).reset_index()

    if maptype is None or len(maptype) == 0:
        warnings.warn("Please specify argument maptype, e.g. 'china'")

    geo = Geo(init_opts=opts.InitOpts(**init_opts))
    geo.add_schema(maptype=maptype)
    for y in ys:
        geo.add(str(y), df[[x, y]].values.tolist())

    geo.set_series_opts(label_opts=opts.LabelOpts(is_show=label_show))
    if visualmap:
        geo.set_global_opts(
                title_opts=opts.TitleOpts(title=title, subtitle=subtitle),
                visualmap_opts=opts.VisualMapOpts(**visualmap_opts)
            )
    else:
        geo.set_global_opts(
                title_opts=opts.TitleOpts(title=title, subtitle=subtitle),
            )
    return geo


def get_map(df,
            x,
            y,
            maptype,
            title,
            subtitle,
            agg_func,
            label_show,
            visualmap,
            visualmap_opts,
            init_opts):
    if agg_func is not None:
        df = df.groupby(x)[y].agg(agg_func).reset_index()

    if maptype is None or len(maptype) == 0:
        warnings.warn("Please specify argument maptype, e.g. 'china'")

    map = (
        Map(init_opts=opts.InitOpts(**init_opts))
        .add(str(y), df[[x, y]].values.tolist(), maptype)
        .set_series_opts(label_opts=opts.LabelOpts(is_show=label_show))
    )

    if visualmap:
        map.set_global_opts(
            title_opts=opts.TitleOpts(title=title, subtitle=subtitle),
            visualmap_opts=opts.VisualMapOpts(**visualmap_opts)
        )
    else:
        map.set_global_opts(
            title_opts=opts.TitleOpts(title=title, subtitle=subtitle),
        )
    return map
