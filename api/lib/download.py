import pyarrow as pa
import pyarrow.compute as pc

from api.constants import FullySupportedBarrierTypes, Scenarios, CUSTOM_TIER_FIELDS
from api.lib.domains import unpack_domains
from api.lib.extract import extract_records
from api.lib.tiers import calculate_tiers


def extract_for_download(
    barrier_type: FullySupportedBarrierTypes,
    unit_ids: dict,
    filters: dict,
    columns: list,
    ranked_only: bool,
    custom_rank: bool,
    sort: Scenarios,
):
    df = extract_records(
        barrier_type,
        unit_ids=unit_ids,
        filters=filters,
        columns=columns,
        ranked_only=ranked_only,
    )

    if len(df) == 0:
        return df

    if barrier_type != "road_crossings":
        # drop species habitat columns that have no useful data
        spp_cols = [c for c in df.column_names if "Habitat" in c and c != "FishHabitatPartnership"]
        drop_cols = [c for c in spp_cols if pc.max(df[c]).as_py() <= 0]
        if len(drop_cols) > 0:
            df = df.drop(drop_cols)

        # calculate custom ranks
        # NOTE: can only calculate ranks for those that have networks and are not excluded from ranking
        if custom_rank:
            to_rank = df.filter(pc.equal(df["Ranked"], True))
            tiers = calculate_tiers(to_rank)
            # cast to int8 to allow setting -1 null values
            tiers = tiers.cast(pa.schema([pa.field(c, "int8") for c in tiers.column_names])).add_column(
                0, to_rank.schema.field("id"), to_rank["id"]
            )

            # join back to full data frame
            df = df.join(tiers, "id")

            if len(to_rank) < len(df):
                # fill missing values
                df = pa.Table.from_pydict(
                    {
                        **{col: df[col] for col in df.column_names if col not in CUSTOM_TIER_FIELDS},
                        **{col: df[col].fill_null(-1) for col in df.column_names if col in CUSTOM_TIER_FIELDS},
                    }
                )

            # Sort by HasNetwork, tier
            df = df.sort_by([("HasNetwork", "descending"), (f"{sort}_tier", "ascending")])

        else:
            # sort only HasNetwork
            df = df.sort_by([("HasNetwork", "descending")])

    df = unpack_domains(df.drop(["id"]))

    return df
