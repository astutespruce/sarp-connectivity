import numpy as np
import pyarrow as pa

from api.constants import DOMAINS, MULTI_VALUE_DOMAINS


def unpack_field(arr, lookup):
    """Unpack domain codes to string values for a single field, using numpy.
    Values that are not present in lookup are assigned empty string.

    Parameters
    ----------
    column : array-like
    lookup : dict
        lookup of codes to values

    Returns
    -------
    np.array
    """
    u, inv = np.unique(arr, return_inverse=True)
    return np.array([lookup.get(x, "") for x in u], dtype=str)[inv].reshape(inv.shape)


def unpack_multivalue_field(arr, lookup):
    """Unpack multi-value domain codes to string values for a single field,
    using numpy. Values that are not present in lookup are assigned empty string.

    This first finds all unique values of the multi-value field, then creates
    a new lookup table for those to their expanded string versions

    Parameters
    ----------
    column : array-like
    lookup : dict
        lookup of codes to values

    Returns
    -------
    np.array
    """

    # expand unique combinations of codes to combinations of values for lookup
    u, inv = np.unique(arr, return_inverse=True)
    expanded_lookup = {
        combination: ", ".join([lookup[k] for k in combination.split(",") if combination]) for combination in u
    }
    return np.array([expanded_lookup.get(x, "") for x in u], dtype=str)[inv].reshape(inv.shape)


def unpack_domains(df):
    """Unpack domain codes to values.

    See analysis.export.lib for version for Pandas DataFrames

    Parameters
    ----------
    df : pyarrow.Table
    """

    schema = df.schema.remove_metadata()
    arrays = []
    for i, field in enumerate(schema.names):
        if field in DOMAINS:
            unpacked = unpack_field(df[field], DOMAINS[field])
            # force domain fields to string type
            schema = schema.set(i, pa.field(field, "string"))

        elif field in MULTI_VALUE_DOMAINS:
            unpacked = unpack_multivalue_field(df[field], MULTI_VALUE_DOMAINS[field])

        else:
            unpacked = df[field]

        arrays.append(unpacked)

    return pa.Table.from_arrays(arrays, schema=schema)
