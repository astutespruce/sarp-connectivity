from api.constants import (
    UNIT_FIELDS,
)


def get_col_types(df, bool_cols=None):
    """Convert pandas types to tippecanoe data types.

    Parameters
    ----------
    df : DataFrame
    bool_cols : set, optional (default: None)
        If present, set of column names that will be set as bool type

    Returns
    -------
    list of ['-T', '<col>:<type'] entries for each column
    """
    out = []
    for col, dtype in df.dtypes.astype("str").to_dict().items():
        if dtype == "geometry":
            continue

        out.append("-T")
        out_type = dtype
        if dtype == "object":
            out_type = "string"
        elif "int" in dtype:
            out_type = "int"
        elif "float" in dtype:
            out_type = "float"

        # overrides
        if bool_cols and col in bool_cols:
            out_type = "bool"

        out.append(f"{col}:{out_type}")

    return out


def to_lowercase(df):
    return df.rename(
        columns={
            k: k.lower()
            for k in df.columns
            if k not in UNIT_FIELDS + ["Subbasin", "Subwatershed"]
        }
    )


def combine_sarpid_name(df):
    df["SARPIDName"] = df.SARPID.fillna("") + "|" + df.Name.fillna("")

    return df.drop(
        columns=[
            "SARPID",
            "Name",
        ]
    )


def fill_na_fields(df):
    str_cols = df.dtypes.loc[df.dtypes == "object"].index
    for col in str_cols:
        df[col] = df[col].fillna("").str.replace('"', "'")
