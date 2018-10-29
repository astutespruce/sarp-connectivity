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

/**
 * Calculate equal interval bins based on number of colors available and min / max of values
 * @param {Array} values - Array of values
 * @param {Array} colors - Array of color hex codes
 *
 * Returns a function that calculates the color for a value.
 */
export const equalIntervals = (values, colors) => {
    const maxValue = Math.max(...values)
    const minValue = Math.min(...values)
    const increment = (maxValue - minValue) / (colors.length - 2)

    return value => {
        for (let i = 0; i < colors.length; i++) {
            if (value < increment * i + minValue) return colors[i]
        }
        return colors[colors.length - 1] // assign top color value
    }
}


/** Convert a 3 or 6 character hex color code to RGB array 
 * @param {String} color - 3 or 6 character hex code, preceded by #.  Example #ABC or #AABBCC
 * 
 * Returns [r, g, b]
*/
export const hexToRGB = (color) => {
    const numDigits = (color.length - 1) / 3
    const colorArray = []
    for (let i=1; i<color.length; i+=numDigits){
        colorArray.push(parseInt(color.slice(i,i+numDigits), 16))
    }
    return colorArray
}



export default { mapColorsToRange, equalIntervals, hexToRGB }
