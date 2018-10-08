import pandas as pd


VALUES = ['AbsoluteGainMi', 'UpstreamMiles', 'DownstreamMiles', 'TotalNetworkMiles', 'PctNatFloodplain',
          'NetworkSinuosity']

COMPOSITE_SCORE_FACTORS = {
    'WatershedConditionScore': [('Sinuosity_Score', 0.5), ('Floodplain_Score', 0.5)],
    'ConnectivityScore': [('AbsGain_Score', 1)],
    'WatershedPlusConnectivityScore': [('WatershedConditionScore', 0.5), ('ConnectivityScore', 0.5)]
}  # Score field and weight


def rank_and_score(huc12s, dams):
    huc12_rows = dams.loc[dams['HUC12'].isin(huc12s)]
    huc12_rows_expanded = huc12_rows

    for value in VALUES:
        extract = huc12_rows[['HUC12', value]]
        extract_sorted = extract.sort_values(by=value, ascending=False)

        counter = 0

        rank_title = '{}_rank_HUC12'.format(value)
        score_title = '{}_score_HUC12'.format(value)

        # Create ranks
        rank_column_values = []

        for n in range(len(extract_sorted)):
            rank_column_values.append(counter)
            counter += 1

        extract_sorted[rank_title] = rank_column_values

        # Create scores
        extract_sorted[score_title] = extract_sorted.apply(lambda row: row[rank_title] / float(counter), axis=1)

        # Join new columns to the main dataframe
        huc12_rows_expanded = huc12_rows_expanded.join(extract_sorted,
                                                       rsuffix='_right').drop(['HUC12_right', '{}_right'.format(value)],
                                                                              axis=1)
    # Create composite scores and tiers

    for score_field in COMPOSITE_SCORE_FACTORS:
        create_composite_scores_tiers(score_field, COMPOSITE_SCORE_FACTORS[score_field], huc12_rows_expanded)

    return huc12_rows_expanded


def create_composite_scores_tiers(label, score_factors, data):
    min_score = 1
    max_score = 0

    # Composite scores

    new_column = []
    for index, row in data.iterrows():
        weighted_scores = [row[field] * weight for i, (field, weight) in enumerate(score_factors)]
        score = sum(weighted_scores)
        new_column.append(score)

        if score < min_score:
            min_score = score
        if score > max_score:
            max_score = score

    data[label] = new_column

    # Tiers

    score_range = max_score - min_score
    score_range = score_range if score_range else 1  # to prevent divide by 0 errors
    tier_thresholds = list(range(95, -5, -5))

    tier_label = '{}_tier'.format(label)
    tier_list = []
    length = 0

    for index, row in data.iterrows():
        length += 1
        score = row[label]
        rel_value = 100 * score / score_range

        for tier_index, threshold in enumerate(tier_thresholds):
            if rel_value >= threshold:
                tier_list.append(tier_index + 1)  # increment since tier_index is 0 based
                break

    data[tier_label] = tier_list

    return


if __name__ == '__main__':
    huc12s = [31300030504, 31300030503, 31300020804, 31300020802]
    dams = pd.read_csv('sarp_dams.csv')
    rank_and_score(huc12s, dams)
