import pyarrow as pa
import pyarrow.compute as pc

from api.constants import FullySupportedBarrierTypes
from api.data import barrier_datasets


def _construct_filter_expr(
    dataset: pa.dataset.Dataset,
    unit_ids: dict,
    filters: dict,
    ranked_only: bool = False,
):
    """Construct pyarrow filter expression for unit ids and field-level filters

    Parameters
    ----------
    dataset : pyarrow Dataset
        dataset that data are being read from
    unit_ids : dict
        dict of {<unit type>:[...unit ids...], ...}
    filters : dict
        dict of {<field>: (<filter type>, <filter values>), ...}
    ranked_only : bool, optional (default: False)
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

    if ranked_only:
        ix = ix & (pc.field("Ranked") == True)  # noqa

    # fields are evaluated using AND logic
    for key, (match_type, values) in filters.items():
        if match_type == "in_dict":
            # find the corresponding dictionary entries so that we can search for these
            # NOTE: we have to read at least 1 record from the dataset to get the dictionary
            dictionary = dataset.scanner(columns=[key]).head(1)[key].combine_chunks().dictionary

            # value filters are combined with OR logic
            matches = dictionary.filter(pc.match_substring(dictionary, values[0]))
            match_ix = pc.is_in(pc.field(key), matches)
            for value in values[1:]:
                matches = dictionary.filter(pc.match_substring(dictionary, value))
                match_ix = match_ix | pc.is_in(pc.field(key), matches)

            ix = ix & match_ix

        else:
            # test that the field value is present in the set of incoming values
            ix = ix & (pc.is_in(pc.field(key), pa.array(values)))

    return ix


def get_record_count(
    barrier_type: FullySupportedBarrierTypes,
    unit_ids: dict,
    filters: dict,
    ranked_only: bool = False,
):
    """Count number of rows in dataset that meet the filter

    Parameters
    ----------
    barrier_type : FullySupportedBarrierTypes
    unit_ids : dict
        dict of {<unit type>:[...unit ids...], ...}
    filters : dict
        dict of {<field>: (<filter type>, <filter values>), ...}
    ranked_only : bool, optional (default: False)
        If true, will limit results to ranked barriers (ones with networks that
        allow ranking, excludes invasive species barriers)

    Returns
    -------
    _type_
        _description_
    """
    dataset = barrier_datasets[barrier_type]
    filter = _construct_filter_expr(dataset, unit_ids, filters, ranked_only=ranked_only)
    scanner = dataset.scanner(columns=[], filter=filter)

    return scanner.count_rows()


def extract_records(
    barrier_type: FullySupportedBarrierTypes,
    unit_ids: dict,
    filters: dict,
    columns: list | None = None,
    ranked_only: bool = False,
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
    ranked_only : bool, optional (default: False)
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
    filter = _construct_filter_expr(dataset, unit_ids, filters, ranked_only=ranked_only)
    scanner = dataset.scanner(columns=columns, filter=filter)

    if as_table:
        return scanner.to_table().combine_chunks()

    return scanner
