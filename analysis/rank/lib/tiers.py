from api.calculate_tiers import calculate_tiers as calculate_tiers_by_unit, SCENARIOS


def calculate_tiers(df):
    # Calculate tiers and scores for the region (None) and State levels
    for group_field in (None, "State"):
        print("Calculating tiers for {}".format(group_field or "Region"))

        tiers_df = calculate_tiers_by_unit(
            df.loc[df.HasNetwork],
            SCENARIOS,
            group_field=group_field,
            prefix="SE" if group_field is None else group_field,
            percentiles=False,
            topn=False,
        )

        # TODO: fixme, seems to have index issues
        df = df.join(tiers_df)

        # Fill n/a with -1 for tiers and cast tier columns to integers
        df[tiers_df.columns] = df[tiers_df.columns].fillna(-1)
        for col in tiers_df.columns:
            if col.endswith("_tier") or col.endswith("_p"):
                df[col] = df[col].astype("int8")
            elif col.endswith("_top"):
                df[col] = df[col].astype("int16")
            elif col.endswith("_score"):
                # Convert to a 100% scale
                df[col] = (df[col] * 100).round().astype("uint16")

    # Tiers are used to display the given barrier on a relative scale
    # compared to other barriers in the state and region.
    # Drop associated raw scores, they are not currently displayed on frontend.
    # df = df.drop(columns=[c for c in df.columns if c.endswith("_score")])

    return df
