import warnings
import numpy as np
from pyecharts.charts import *
from pyecharts import options as opts
from pyecharts.commons.utils import JsCode

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
                    new_kwargs["subtitle"] = f"{new_kwargs['subtitle']}{by}={by_value}", 
                    chart_ = func(**new_kwargs)
                    page.add(chart_)
                return page
            else:
                return func(**kwargs)
        return inner
    return wrapper


def timeline_decorator(timeline=None, timeline_opts={}):
    def wrapper(func):
        def inner(**kwargs):
            if timeline is not None:
                tl = Timeline(**timeline_opts)
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


def get_pie(df, x, y, title, subtitle, label_show, agg_func, legend_opts):
    # TODO: 是否需要像legend_opts，对每个opts使用额外的dict自定义接口，使得用户可以自定义
    if agg_func is not None:
        df = df.groupby(x)[y].agg(agg_func).reset_index()
    pie = (
        Pie()
        .add(str(y), df[[x, y]].values.tolist())
        .set_series_opts(
            label_opts=opts.LabelOpts(formatter="{b}:{d}%", position="inner", is_show=label_show))
        .set_global_opts(
            title_opts=opts.TitleOpts(title=title, subtitle=subtitle),
            legend_opts=opts.LegendOpts(**legend_opts),
        )
    )
    return pie


def get_bar(df, x, ys, xaxis_name, yaxis_name, title, subtitle, agg_func, stack_view, reverse_axis, label_show):
    if stack_view:
        stack = ["1"]*len(ys)
    else:
        stack = [str(i) for i in range(1, len(ys)+1)]

    if agg_func is not None:
        df = df.groupby(x)[ys].agg(agg_func).reset_index()

    bar = (
        Bar()
        .add_xaxis(df[x].values.tolist())
    )

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
        title_opts=opts.TitleOpts(title=title, subtitle=subtitle)
    )
    if reverse_axis:
        bar.reversal_axis()
    return bar


def get_bar3d(df, x, y, z, title, subtitle):
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
            visualmap_opts=opts.VisualMapOpts(max_=df[z].max()),
            title_opts=opts.TitleOpts(title=title, subtitle=subtitle)
        )
    )
    return bar3d


def get_line(df, x, ys, xtype, xaxis_name, yaxis_name, title, subtitle, agg_func, smooth, label_show):
    if agg_func is not None:
        df = df.groupby(x)[ys].agg(agg_func).reset_index()

    df = df.sort_values(by=x)
    line = (
        Line()
        .add_xaxis(df[x].values.tolist())
    )

    for y in ys:
        line.add_yaxis(str(y), df[y].values.tolist(),
                        is_smooth=smooth)

    line.set_series_opts(
        label_opts=opts.LabelOpts(is_show=label_show)
    )

    if xtype is None:
        if df[x].values.dtype.type is np.str_:
            xtype = "category"
        else:
            xtype = "value"
        warnings.warn(f"Please specify argument xtype, '{xtype}' is infered!")
    
    line.set_global_opts(
        xaxis_opts=opts.AxisOpts(name=xaxis_name, type_=xtype),
        yaxis_opts=opts.AxisOpts(name=yaxis_name, type_="value"),
        title_opts=opts.TitleOpts(title=title, subtitle=subtitle)
    )
    return line


def get_scatter(df, x, ys, xtype, xaxis_name, yaxis_name, title, subtitle, agg_func, label_show):
    if agg_func is not None:
        df = df.groupby(x)[ys].agg(agg_func).reset_index()

    scatter = (
        Scatter()
        .add_xaxis(df[x].values.tolist())
    )

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
        warnings.warn(f"Please specify argument xtype, \'{xtype}\' is infered!")

    scatter.set_global_opts(
        xaxis_opts=opts.AxisOpts(name=xaxis_name, type_=xtype),
        yaxis_opts=opts.AxisOpts(name=yaxis_name, type_="value"),
        title_opts=opts.TitleOpts(title=title, subtitle=subtitle)
    )
    return scatter