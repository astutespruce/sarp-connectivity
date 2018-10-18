/**
 * Calculate equal interval bins
 *
 * @param {Array} range - [minValue, maxValue]
 * @param {Array} numIntervals - number of intervals to calculate
 *
 * Returns intervals [[minValue, minValue + interval], [minValue + interval]... [maxValue-interval, maxValue]].
 */
export const equalIntervals = (range, numIntervals) => {
    const [minValue, maxValue] = range
    const increment = (maxValue - minValue) / numIntervals
    return Array.from({ length: numIntervals }, (_, i) => [i * increment + minValue, (i + 1) * increment + minValue])
}

export default { equalIntervals }
