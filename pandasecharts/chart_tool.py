import warnings
import numpy as np
from pyecharts.charts import Page, Timeline
from pyecharts.charts import Line, Bar, Pie, Scatter
from pyecharts.charts import Line3D, Bar3D, Scatter3D
from pyecharts.charts import Boxplot, Funnel, Geo, Map
from pyecharts import options as opts
from .data_tool import infer_dtype


# TODO: 图标的点支持自定义类型，比如line geo里的点形状

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
    cat2region = dict(
        zip(range(1, cat_bins+1), zip(bin_edges[:-1], bin_edges[1:])))
    region_a = [cat2region[min(c, cat_bins)] for c in cat_a]
    return region_a


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


def timeline_decorator(timeline=None, timeline_opts={}, theme=None):
    def wrapper(func):
        def inner(**kwargs):
            if timeline is not None:
                if theme is not None:
                    tl = Timeline(init_opts=opts.InitOpts(theme=theme))
                else:
                    tl = Timeline()
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
            agg_func,
            legend_opts,
            theme):
    if agg_func is not None:
        df = df.groupby(x)[y].agg(agg_func).reset_index()

    if theme is not None:
        pie = Pie(init_opts=opts.InitOpts(theme=theme))
    else:
        pie = Pie()

    pie = (
        pie
        .add(str(y), df[[x, y]].values.tolist())
        .set_series_opts(
            label_opts=opts.LabelOpts(
                formatter="{b}:{d}%",
                position="inner",
                is_show=label_show)
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
            agg_func,
            stack_view,
            reverse_axis,
            label_show,
            legend_opts,
            theme):
    if stack_view:
        stack = ["1"]*len(ys)
    else:
        stack = [str(i) for i in range(1, len(ys)+1)]

    if agg_func is not None:
        df = df.groupby(x)[ys].agg(agg_func).reset_index()

    if theme is not None:
        bar = Bar(init_opts=opts.InitOpts(theme=theme))
    else:
        bar = Bar()

    bar = bar.add_xaxis(df[x].values.tolist())
    for y, st in zip(ys, stack):
        bar.add_yaxis(str(y), df[y].values.tolist(), stack=st)

    bar.set_series_opts(
        label_opts=opts.LabelOpts(
            position="right" if stack_view or reverse_axis else "top",
            is_show=label_show
        ),
    )
    bar.set_global_opts(
        xaxis_opts=opts.AxisOpts(name=xaxis_name, type_='category'),
        yaxis_opts=opts.AxisOpts(name=yaxis_name, type_='value'),
        title_opts=opts.TitleOpts(title=title, subtitle=subtitle),
        legend_opts=opts.LegendOpts(**legend_opts),
    )
    if reverse_axis:
        bar.reversal_axis()
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
              theme):

    if theme is not None:
        bar3d = Bar3D(init_opts=opts.InitOpts(theme=theme))
    else:
        bar3d = Bar3D()

    bar3d = (
        bar3d
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
             xaxis_name,
             yaxis_name,
             title,
             subtitle,
             agg_func,
             smooth,
             label_show,
             legend_opts,
             theme):
    if agg_func is not None:
        df = df.groupby(x)[ys].agg(agg_func).reset_index()

    df = df.sort_values(by=x)

    if theme is not None:
        line = Line(init_opts=opts.InitOpts(theme=theme))
    else:
        line = Line()

    line = line.add_xaxis(df[x].values.tolist())

    for y in ys:
        line.add_yaxis(str(y), df[y].values.tolist(),
                       is_smooth=smooth)

    line.set_series_opts(
        label_opts=opts.LabelOpts(is_show=label_show)
    )

    if xtype is None:
        xtype = infer_dtype(df[x])
        warnings.warn(f"Please specify argument xtype, '{xtype}' is infered!")

    line.set_global_opts(
        xaxis_opts=opts.AxisOpts(name=xaxis_name, type_=xtype),
        yaxis_opts=opts.AxisOpts(name=yaxis_name, type_="value"),
        title_opts=opts.TitleOpts(title=title, subtitle=subtitle),
        legend_opts=opts.LegendOpts(**legend_opts),
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
               theme):
    if xtype is None:
        xtype = infer_dtype(df[x])
        warnings.warn(f"Please specify argument xtype, '{xtype}' is infered!")
    if ytype is None:
        ytype = infer_dtype(df[x])
        warnings.warn(f"Please specify argument ytype, '{ytype}' is infered!")
    if ztype is None:
        ztype = infer_dtype(df[x])
        warnings.warn(f"Please specify argument ztype, '{ztype}' is infered!")

    if theme is not None:
        line3d = Line3D(init_opts=opts.InitOpts(theme=theme))
    else:
        line3d = Line3D()

    line3d = (
        line3d
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
                legend_opts,
                visualmap,
                visualmap_opts,
                theme):
    if agg_func is not None:
        df = df.groupby(x)[ys].agg(agg_func).reset_index()

    if theme is not None:
        scatter = Scatter(init_opts=opts.InitOpts(theme=theme))
    else:
        scatter = Scatter()
    scatter.add_xaxis(df[x].values.tolist())

    for y in ys:
        scatter.add_yaxis(str(y), df[y].values.tolist())

    scatter.set_series_opts(
        label_opts=opts.LabelOpts(is_show=label_show)
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
                  theme):
    if xtype is None:
        xtype = infer_dtype(df[x])
        warnings.warn(f"Please specify argument xtype, '{xtype}' is infered!")
    if ytype is None:
        ytype = infer_dtype(df[x])
        warnings.warn(f"Please specify argument ytype, '{ytype}' is infered!")
    if ztype is None:
        ztype = infer_dtype(df[x])
        warnings.warn(f"Please specify argument ztype, '{ztype}' is infered!")

    if theme is not None:
        scatter3d = Scatter3D(init_opts=opts.InitOpts(theme=theme))
    else:
        scatter3d = Scatter3D()
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
                theme):
    if theme is not None:
        boxplot = Boxplot(init_opts=opts.InitOpts(theme=theme))
    else:
        boxplot = Boxplot()

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
               theme):
    if theme is not None:
        funnel = Funnel(init_opts=opts.InitOpts(theme=theme))
    else:
        funnel = Funnel()

    funnel = (
        funnel
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
            theme):
    if agg_func is not None:
        df = df.groupby(x)[ys].agg(agg_func).reset_index()

    if maptype is None or len(maptype) == 0:
        warnings.warn("Please specify argument maptype, e.g. 'china'")

    if theme is not None:
        geo = Geo(init_opts=opts.InitOpts(theme=theme))
    else:
        geo = Geo()
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
            theme):
    if agg_func is not None:
        df = df.groupby(x)[y].agg(agg_func).reset_index()

    if maptype is None or len(maptype) == 0:
        warnings.warn("Please specify argument maptype, e.g. 'china'")

    if theme is not None:
        map = Map(init_opts=opts.InitOpts(theme=theme))
    else:
        map = Map()
    map = (
        map
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
