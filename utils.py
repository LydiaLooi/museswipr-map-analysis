def weighted_average_of_values(
    values, top_percentage=0.3, top_weight=0.7, bottom_weight=0.3
):
    # Find the threshold that separates the top 30% highest densities from the rest
    threshold_index = int(len(values) * (1 - top_percentage))
    moving_averages_sorted = sorted(values, reverse=True)
    threshold = moving_averages_sorted[threshold_index]

    # Calculate the weighted average
    total_weight = 0
    weighted_sum = 0

    for avg in values:
        if avg >= threshold:
            weight = top_weight
        else:
            weight = bottom_weight

        weighted_sum += avg * weight
        total_weight += weight

    weighted_average = weighted_sum / total_weight
    return weighted_average
