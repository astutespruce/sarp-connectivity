import numpy as np

from api.constants import DOMAINS, MULTI_VALUE_DOMAINS


def unpack_domains(df):
    """Unpack domain codes to values.

    Parameters
    ----------
    df : DataFrame
    """

    df = df.copy()
    for field, domain in DOMAINS.items():
        if field in df.columns:
            u, inv = np.unique(df[field].values, return_inverse=True)
            df[field] = np.array([domain.get(x, "") for x in u], dtype=str)[inv].reshape(inv.shape)

    for field, domain in MULTI_VALUE_DOMAINS.items():
        if field in df.columns:
            # expand unique combinations of codes to combinations of values for lookup
            u, inv = np.unique(df[field].values, return_inverse=True)
            expanded_lookup = {
                combination: ", ".join([domain[k] for k in combination.split(",") if combination]) for combination in u
            }
            df[field] = np.array([expanded_lookup.get(x, "") for x in u], dtype=str)[inv].reshape(inv.shape)

    return df
