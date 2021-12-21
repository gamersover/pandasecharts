import warnings

options = {}


options["max_bins"] = 50


def set_options(key, value):
    options[key] = value


def get_options(key):
    if key in options:
        return options[key]
    else:
        warnings.warn(f"There is no key {key} in options")
