export const hasCoordsRegex = /(\d+)[\s\w°'"-.]*,[\s\w°'"-.]*(\d+)/g

const parseValue = (value: string, isLatitude = false) => {
	const directionMatch = /[NSEW]/g.exec(value)
	const direction = directionMatch ? directionMatch[0] : null
	let factor = 1
	if (direction === 'S' || direction === 'W') {
		factor = -1
	}

	let decimalDegrees = null

	if (/[°'" ]/g.test(value)) {
		// drop blank parts
		const parts = value.split(/[^\d.-]+/).filter((p) => !!p)
		if (parts.length === 0) {
			return { isValid: false, invalidReason: 'Format is incorrect' }
		}
		const [rawDegrees, rawMinutes, rawSeconds] = parts
		const degrees = parseFloat(rawDegrees)
		const minutes = parseFloat(rawMinutes || '0')
		const seconds = parseFloat(rawSeconds || '0')

		if (minutes < 0 || minutes > 60) {
			return {
				isValid: false,
				invalidReason: 'Minutes are out of bounds (must be 0-60)'
			}
		}

		if (seconds < 0 || seconds > 60) {
			return {
				isValid: false,
				invalidReason: 'Seconds are out of bounds (must be 0-60)'
			}
		}

		if (degrees < 0) {
			decimalDegrees = factor * (degrees - minutes / 60 - seconds / 3600)
		} else {
			decimalDegrees = factor * (degrees + minutes / 60 + seconds / 3600)
		}
	} else {
		const decimalMatch = /[\d+.*-]+/g.exec(value)
		if (decimalMatch) {
			decimalDegrees = factor * parseFloat(decimalMatch[0])
		} else {
			return {
				isValid: false,
				invalidReason: 'Format is incorrect'
			}
		}
	}

	let invalidReason = null

	let isWithinBounds = true
	if (decimalDegrees !== null) {
		if (isLatitude) {
			if (!(decimalDegrees <= 90 && decimalDegrees >= -90)) {
				isWithinBounds = false
				invalidReason = 'Latitude is out of bounds (must be -90 to 90)'
			}
		} else if (!(decimalDegrees <= 180 && decimalDegrees >= -180)) {
			isWithinBounds = false
			invalidReason = 'Longitude is out of bounds (must be -180 to 180)'
		}
	}

	return {
		decimalDegrees,
		isValid: decimalDegrees !== null && isWithinBounds,
		invalidReason
	}
}

export const parseLatLon = (value: string) => {
	if (value.search(hasCoordsRegex) === -1) {
		return { isValid: false }
	}

	const [rawLat, rawLon] = value.toUpperCase().split(',')
	if (rawLat === undefined || rawLon === undefined) {
		return {
			isValid: false
		}
	}

	const {
		decimalDegrees: lat,
		isValid: isLatValid,
		invalidReason: invalidLatReason
	} = parseValue(rawLat.trim(), true)
	const {
		decimalDegrees: lon,
		isValid: isLonValid,
		invalidReason: invalidLonReason
	} = parseValue(rawLon.trim(), false)

	return {
		lat,
		lon,
		isValid: isLatValid && isLonValid,
		invalidReason: invalidLatReason || invalidLonReason
	}
}
