import pyecharts.options as opts


class ChartConfig:
    def get_init_opts(self, init_opts, theme, figsize):
        if init_opts is None:
            init_opts = {}
        init_opts_ = {}
        if theme is not None:
            init_opts_["theme"] = theme
        if figsize is not None:
            init_opts_["width"] = f"{figsize[0]}px"
            init_opts_["height"] = f"{figsize[1]}px"
        init_opts_.update(init_opts)
        return init_opts_

    def get_label_opts(self, label_opts, label_show,
                       position=None, formatter=None):
        if label_opts is None:
            label_opts = {}
        label_opts_ = {
            "is_show": label_show
        }
        if position is not None:
            label_opts_["position"] = position
        if formatter is not None:
            label_opts_["formatter"] = formatter
        label_opts_.update(label_opts)
        return label_opts_

    def get_title_opts(self, title_opts, title, subtitle):
        if title_opts is None:
            title_opts = {}
        title_opts_ = {
            "title": title,
            "subtitle": subtitle
        }
        title_opts_.update(title_opts)
        return title_opts_

    def get_legend_opts(self, legend_opts):
        if legend_opts is None:
            legend_opts = {}
        return legend_opts

    def get_axis_opts(self, axis_opts, axis_name, type_=None):
        if axis_opts is None:
            axis_opts = {}
        axis_opts_ = {
            "name": axis_name,
        }
        if type_ is not None:
            axis_opts_["type_"] = type_

        axis_opts_.update(axis_opts)
        return axis_opts_

    def get_visualmap_opts(self, visualmap_opts):
        if visualmap_opts is None:
            visualmap_opts = {}
        return visualmap_opts


class PieConfig(ChartConfig):
    def get_label_opts(self, label_opts, label_show):
        formatter = "{b}:{d}%"
        position = "inner"
        return super().get_label_opts(label_opts, label_show,
                                      position, formatter)

    def get_pie_opts(self, pie_opts, center, radius, rosetype):
        if pie_opts is None:
            pie_opts = {}
        pie_opts_ = {
            "center": center,
            "radius": radius,
            "rosetype": rosetype
        }
        pie_opts_.update(pie_opts)
        return pie_opts_


class BarConfig(ChartConfig):
    def get_label_opts(self, label_opts, label_show, position):
        position = "right" if position else "top"
        return super().get_label_opts(label_opts, label_show, position)

    def get_xaxis_opts(self, xaxis_opts, xaxis_name, multiple_yaxis):
        if xaxis_opts is None:
            xaxis_opts = {}
        xaxis_opts_ = {}
        if multiple_yaxis:
            xaxis_opts_ = {
                "axispointer_opts": opts.AxisPointerOpts(is_show=True,
                                                         type_="shadow"),
            }
        xaxis_opts_.update(xaxis_opts)
        return self.get_axis_opts(xaxis_opts_, xaxis_name, "category")

    def get_yaxis_opts(self, yaxis_opts, yaxis_name):
        return self.get_axis_opts(yaxis_opts, yaxis_name, "value")

    def get_tooltip_opts(self, tooltip_opts, multiple_yaxis):
        if tooltip_opts is None:
            tooltip_opts = {}
        tooltip_opts_ = {}
        if multiple_yaxis:
            tooltip_opts_ = {
                "trigger": "axis",
                "axis_pointer_type": "cross"
            }
        tooltip_opts_.update(tooltip_opts)
        return tooltip_opts_


class Bar3DConfig(ChartConfig):
    def get_xaxis_opts(self, xaxis_opts, xaxis_name):
        return self.get_axis_opts(xaxis_opts, xaxis_name, "category")

    def get_yaxis_opts(self, yaxis_opts, yaxis_name):
        return self.get_axis_opts(yaxis_opts, yaxis_name, "category")

    def get_zaxis_opts(self, zaxis_opts, zaxis_name):
        return self.get_axis_opts(zaxis_opts, zaxis_name, "value")


class LineConfig(ChartConfig):
    def get_xaxis_opts(self, xaxis_opts, xaxis_name, xtype):
        return self.get_axis_opts(xaxis_opts, xaxis_name, xtype)

    def get_yaxis_opts(self, yaxis_opts, yaxis_name):
        return self.get_axis_opts(yaxis_opts, yaxis_name, "value")

    def get_tooltip_opts(self, tooltip_opts, multiple_yaxis):
        if tooltip_opts is None:
            tooltip_opts = {}
        tooltip_opts_ = {}
        if multiple_yaxis:
            tooltip_opts_ = {
                "trigger": "axis",
                "axis_pointer_type": "cross"
            }
        tooltip_opts_.update(tooltip_opts)
        return tooltip_opts_


class Line3DConfig(ChartConfig):
    def get_xaxis_opts(self, xaxis_opts, xaxis_name, xtype):
        return self.get_axis_opts(xaxis_opts, xaxis_name, xtype)

    def get_yaxis_opts(self, yaxis_opts, yaxis_name, ytype):
        return self.get_axis_opts(yaxis_opts, yaxis_name, ytype)

    def get_zaxis_opts(self, zaxis_opts, zaxis_name, ztype):
        return self.get_axis_opts(zaxis_opts, zaxis_name, ztype)


class ScatterConfig(ChartConfig):
    def get_xaxis_opts(self, xaxis_opts, xaxis_name, xtype):
        return self.get_axis_opts(xaxis_opts, xaxis_name, xtype)

    def get_yaxis_opts(self, yaxis_opts, yaxis_name):
        return self.get_axis_opts(yaxis_opts, yaxis_name, "value")


class Scatter3DConfig(ChartConfig):
    def get_xaxis_opts(self, xaxis_opts, xaxis_name, xtype):
        return self.get_axis_opts(xaxis_opts, xaxis_name, xtype)

    def get_yaxis_opts(self, yaxis_opts, yaxis_name, ytype):
        return self.get_axis_opts(yaxis_opts, yaxis_name, ytype)

    def get_zaxis_opts(self, zaxis_opts, zaxis_name, ztype):
        return self.get_axis_opts(zaxis_opts, zaxis_name, ztype)


class BoxplotConfig(ChartConfig):
    def get_xaxis_opts(self, xaxis_opts, xaxis_name):
        return self.get_axis_opts(xaxis_opts, xaxis_name)

    def get_yaxis_opts(self, yaxis_opts, yaxis_name):
        return self.get_axis_opts(yaxis_opts, yaxis_name)


class FunnelConfig(ChartConfig):
    pass


class GeoConfig(ChartConfig):
    pass


class MapConfig(ChartConfig):
    pass
