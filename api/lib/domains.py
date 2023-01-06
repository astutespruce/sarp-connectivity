import numpy as np
import pyarrow as pa

from api.constants import DOMAINS


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


def unpack_domains(df):
    """Unpack domain codes to values.

    See analysis.export.lib for version for Pandas DataFrames

    Parameters
    ----------
    df : pyarrow.Table
    """

    schema = df.schema.remove_metadata()
    arrays = [
        unpack_field(df[field], DOMAINS[field]) if field in DOMAINS else df[field]
        for field in schema.names
    ]

    for i, field in enumerate(schema.names):
        if field in DOMAINS:
            schema = schema.set(i, pa.field(field, "string"))

    return pa.Table.from_arrays(
        arrays,
        schema=schema,
    )
