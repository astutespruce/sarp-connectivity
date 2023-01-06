from pyogrio import read_info


def get_column_names(gdb, layer, columns):
    """Get correct column names to read from layer and dictc to convert them
    back to requested names.

    Column names vary between NHD Plus HR versions.  Beta version used TitleCase
    for all columns, Current verison uses mostly lowercase.

    Parameters
    ----------
    gdb : Path or str
    layer : str
    columns : list-like
        column names to read from layer

    Returns
    -------
    list, dict
        list of column names to read from layer, dict to convert them to requested
        names
    """

    available_columns = read_info(gdb, layer=layer)["fields"]
    all_found = [c for c in columns if c in available_columns]

    # all columns are found with same casing, return them
    if len(all_found) == len(columns):
        return columns, {}

    lower_map = {c.lower(): c for c in available_columns}
    # create mapping of requested name to matching name in dataset
    name_map = {c: lower_map[c.lower()] for c in columns if c.lower() in lower_map}
    missing = [c for c in columns if not c in name_map]
    if missing:
        raise ValueError(f"Could not find columns {missing} in {gdb} layer={layer}")

    # invert the name map to go from the names read back to names requested
    return list(name_map.values()), {v: k for k, v in name_map.items()}
