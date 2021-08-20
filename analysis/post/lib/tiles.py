def get_col_types(df):
    out = []
    for col, dtype in df.dtypes.astype("str").to_dict().items():
        out.append("-T")
        out_type = dtype
        if dtype == "object":
            out_type = "string"
        elif "int" in dtype:
            out_type = "int"
        elif "float" in dtype:
            out_type = "float"

        out.append(f"{col}:{out_type}")

    return out
