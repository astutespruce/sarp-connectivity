from api.constants import DOMAINS


def unpack_domains(df):
    """Unpack domain codes to values.

    Parameters
    ----------
    df : DataFrame
    """

    df = df.copy()
    for field, domain in DOMAINS.items():
        if field in df.columns:
            df[field] = df[field].map(domain)

    return df
