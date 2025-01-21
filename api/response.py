from io import BytesIO
from zipfile import ZipFile, ZIP_DEFLATED

from fastapi.responses import Response
from pyarrow.feather import write_feather
from pyarrow.csv import write_csv


def csv_response(df, bounds=None):
    """Write data frame to CSV and return Response with proper headers

    Parameters
    ----------
    df : pyarrow Table
    bounds : list-like of [xmin, ymin, xmax, ymax], optional (default: None)

    Returns
    -------
    fastapi Response
    """

    csv_stream = BytesIO()
    cols = [c.lower() for c in df.schema.names]
    write_csv(df.rename_columns(cols).combine_chunks(), csv_stream)

    response = Response(content=csv_stream.getvalue(), media_type="text/csv")

    if bounds is not None:
        response.headers["X-BOUNDS"] = ",".join(str(b) for b in bounds)

    return response


def feather_response(df, bounds=None):
    """Write data frame to feather (Arrow IPC) and return Response with proper headers

    Parameters
    ----------
    df : pyarrow Table
    bounds : list-like of [xmin, ymin, xmax, ymax], optional (default: None)

    Returns
    -------
    fastapi Response
    """

    cols = [c.lower() for c in df.schema.names]
    table = df.rename_columns(cols)

    # discard pandas metadata and set bounds
    table = table.replace_schema_metadata({"bounds": ",".join(str(b) for b in bounds) if bounds is not None else ""})

    stream = BytesIO()
    write_feather(
        table,
        stream,
        # Feather format in JS Arrow lib does not yet support compressed
        compression="uncompressed",
    )
    response = Response(content=stream.getvalue(), media_type="application/octet-stream")

    return response
