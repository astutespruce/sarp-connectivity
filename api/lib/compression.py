def pack_bits(df, field_bits):
    """Pack categorical values into a single integer.

    See analysis.lib.util::pack_bits for a version that can take Pandas DataFrames

    All values must fit within a uint32.

    `value_shift` is optional (default: 0); if present it is the amount that
    is added to 0 to reach minimum value of value range for unpacked value.

    Parameters
    ----------
    df : pyarrow.Table
    field_bits : list-like of dicts
        {"field": <field>, "bits": <num bits>, "value_shift": <shift>} for each field

    Returns
    -------
    ndarray of dtype large enough to hold all values
    """

    tot_bits = sum([f["bits"] for f in field_bits])
    dtype = "uint32"
    if tot_bits <= 8:
        dtype = "uint8"
    elif tot_bits <= 16:
        dtype = "uint16"
    elif tot_bits > 32:
        dtype = "uint64"
        # cannot bit-shift 64 bit integers in JS
        raise ValueError(f"Packing requires {tot_bits} bits; needs to be less than 32")

    first = field_bits[0]
    values = df[first["field"]].to_numpy()
    values = values - first.get("value_shift", 0)
    if values.min() < 0:
        raise ValueError(f"Values for {first['field']} must be >= 0")

    values = values.astype(dtype)
    if values.max() > (2 ** first["bits"]) - 1:
        raise ValueError(f"Values for {first['field']} cannot be stored in {first['bits']} bits")

    sum_bits = first["bits"]
    for entry in field_bits[1:]:
        field_values = df[entry["field"]].to_numpy()
        field_values = field_values - entry.get("value_shift", 0)
        if field_values.min() < 0:
            raise ValueError(f"Values for {entry['field']} must be >= 0")

        if field_values.max() > (2 ** entry["bits"]) - 1:
            raise ValueError(f"Values for {first['field']} cannot be stored in {entry['bits']} bits")

        values = values | field_values.astype(dtype) << sum_bits
        sum_bits += entry["bits"]

    return values
