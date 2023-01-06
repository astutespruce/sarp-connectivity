def format_log(status, field, values):
    if len(values) == 1:
        value = values[0]
        if value == "":
            value = "''"
        return f"{status}: {field} == {value}"

    return f"{status}: {field} one of {values}"
