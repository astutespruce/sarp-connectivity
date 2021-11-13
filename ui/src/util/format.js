export const formatPercent = (percent) => {
  if (percent === 0) {
    return '0'
  }
  if (percent < 1) {
    return '< 1'
  }
  if (percent < 5) {
    // round to nearest 1 decimal place
    return Math.round(percent * 10) / 10
  }
  if (percent > 99 && percent < 100) {
    return '> 99' // it looks odd to have 100% stack up next to categories with <1
  }
  return Math.round(percent)
}

export const formatNumber = (number, decimals = null, auto = false) => {
  const absNumber = Math.abs(number)
  let targetDecimals = decimals
  // guess number of decimals based on magnitude
  if (targetDecimals === null || auto) {
    if (absNumber > 100 || Math.round(absNumber) === absNumber) {
      targetDecimals = 0
    } else if (absNumber > 10) {
      targetDecimals = 1
    } else if (absNumber > 1) {
      targetDecimals = 2
    } else {
      targetDecimals = 3
    }
  }

  console.log(
    'format: ',
    number,
    'decimals:',
    decimals,
    'targetDecimals:',
    targetDecimals
  )

  // targetDecimals = Math.min(targetDecimals, decimals || 0)

  if (auto) {
    targetDecimals = Math.min(targetDecimals, decimals || 10)
  }

  const factor = 10 ** targetDecimals

  // format to localeString, and manually set the desired number of decimal places
  let formatted = (Math.round(number * factor) / factor).toLocaleString(
    undefined,
    {
      minimumFractionDigits: targetDecimals,
      maximumFractionDigits: targetDecimals,
    }
  )
  // trim trailing 0's after decimal
  if (
    formatted.length > 1 &&
    formatted.indexOf('.') > 0 &&
    formatted.endsWith('0')
  ) {
    formatted = formatted.slice(0, formatted.length - 1)
  }
  if (formatted.endsWith('.')) {
    formatted = formatted.slice(0, formatted.length - 1)
  }
  return formatted
}

export const capitalize = (word) =>
  `${word.slice(0, 1).toUpperCase()}${word.slice(1)}`

export const toCamelCase = (value) => {
  if (!value) return value

  return value
    .split('_')
    .map((part, i) => (i === 0 ? part : capitalize(part)))
    .join('')
}
