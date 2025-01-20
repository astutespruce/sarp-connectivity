import pyarrow as pa
import pyarrow.compute as pc

from api.constants import FullySupportedBarrierTypes
from api.data import barrier_datasets


def _construct_filter_expr(
    unit_ids: dict,
    filters: dict,
    ranked: bool = False,
):
    """Construct pyarrow filter expression for unit ids and field-level filters

    Parameters
    ----------
    unit_ids : dict
        dict of {<unit type>:[...unit ids...], ...}
    filters : dict
        dict of {<field>: (<filter type>, <filter values>), ...}
    ranked : bool, optional (default: False)
        If true, will limit results to ranked barriers (ones with networks that
        allow ranking, excludes invasive species barriers)
    """
    # evaluate unit ids using OR logic
    layers = list(unit_ids.keys())

    if len(layers):
        ix = pc.field(layers[0]).isin(unit_ids[layers[0]])
        for layer in layers[1:]:
            ix = ix | pc.field(layer).isin(unit_ids[layer])
    else:
        # filter only by other filters instead of units
        ix = pc.scalar(True)

    if ranked:
        ix = ix & (pc.field("Ranked") == True)  # noqa

    # fields are evaluated using AND logic
    for key, (match_type, values) in filters.items():
        if match_type == "in_string":
            # test if incoming string is present within the set of comma-delimited
            # values in the field using OR logic
            match_ix = pc.match_substring(pc.field(key), values[0])
            for value in values[1:]:
                match_ix = match_ix | pc.match_substring(pc.field(key), value)

            ix = ix & match_ix

        else:
            # test that the field value is present in the set of incoming values
            ix = ix & (pc.is_in(pc.field(key), pa.array(values)))

    return ix


def count_records(
    barrier_type: FullySupportedBarrierTypes,
    unit_ids: dict,
    filters: dict,
    ranked: bool = False,
):
    """Count number of rows in dataset that meet the filter

    Parameters
    ----------
    barrier_type : FullySupportedBarrierTypes
    unit_ids : dict
        dict of {<unit type>:[...unit ids...], ...}
    filters : dict
        dict of {<field>: (<filter type>, <filter values>), ...}
    ranked : bool, optional (default: False)
        If true, will limit results to ranked barriers (ones with networks that
        allow ranking, excludes invasive species barriers)

    Returns
    -------
    _type_
        _description_
    """
    dataset = barrier_datasets[barrier_type]
    filter = _construct_filter_expr(unit_ids, filters, ranked=ranked)
    scanner = dataset.scanner(columns=[], filter=filter)

    return scanner.count_rows()


def extract_records(
    barrier_type: FullySupportedBarrierTypes,
    unit_ids: dict,
    filters: dict,
    columns: list | None = None,
    ranked: bool = False,
    as_table: bool = True,
):
    """Extract records from the pyarrow dataset corresponding to barrier_type,
    and return the associated pyarrow Scanner or Table (with chunks combined)

    Parameters
    ----------
    barrier_type : FullySupportedBarrierTypes
    unit_ids : dict
        dict of {<unit type>:[...unit ids...], ...}
    filters : dict
        dict of {<field>: (<filter type>, <filter values>), ...}
    columns : list, optional (default: None)
        list of column names to include in output; if None, will return all columns
    ranked : bool, optional (default: False)
        If true, will limit results to ranked barriers (ones with networks that
        allow ranking, excludes invasive species barriers)
    as_table : bool, optional (default: True)
        If True, will return the pyarrow Table, which will materialize all records.
        If False, will return the pyarrow Scanner, which can be scanned in batches.

    Returns
    -------
    pyarrow Dataset or Scanner
    """

    dataset = barrier_datasets[barrier_type]
    filter = _construct_filter_expr(unit_ids, filters, ranked=ranked)
    scanner = dataset.scanner(columns=columns, filter=filter)

    if as_table:
        return scanner.to_table().combine_chunks()

    return scanner
