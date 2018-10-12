/**
 *
 * @param {Array} colors - Array of color hex codes
 * @param {Array} range - [minValue, maxValue]
 *
 * Returns a flat listing of value and color: [value, color, value2, color2,...]
 */
export const mapColorsToRange = (colors, range) => {
    const [minValue, maxValue] = range
    const increment = (maxValue - minValue) / (colors.length - 2)
    let out = []
    colors.forEach((color, i) => {
        out = out.concat([increment * i + minValue, color])
    })
    return out
}

export default { mapColorsToRange }
