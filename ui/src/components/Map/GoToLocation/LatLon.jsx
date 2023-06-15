import React, { useState, useCallback, forwardRef } from 'react'
import PropTypes from 'prop-types'
import { Box, Flex, Input, Text, Button } from 'theme-ui'
import {
  SearchLocation,
  Times,
  ExclamationTriangle,
} from '@emotion-icons/fa-solid'

const invalidInputCSS = {
  borderColor: 'accent',
  borderWidth: '1px 0.5rem 1px 1px',
}

const hasCoordsRegex = /(\d+)[\s\w°'"-.]*,[\s\w°'"-.]*(\d+)/g

const parseValue = (value, isLatitude = false) => {
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
    let [degrees, minutes, seconds] = parts
    degrees = parseFloat(degrees)
    minutes = parseFloat(minutes || 0)
    seconds = parseFloat(seconds || 0)

    if (minutes < 0 || minutes > 60) {
      return {
        isValid: false,
        invalidReason: 'Minutes are out of bounds (must be 0-60)',
      }
    }

    if (seconds < 0 || seconds > 60) {
      return {
        isValid: false,
        invalidReason: 'Seconds are out of bounds (must be 0-60)',
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
        invalidReason: 'Format is incorrect',
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
    invalidReason,
  }
}

const parseLatLon = (value) => {
  if (value.search(hasCoordsRegex) === -1) {
    return { isValid: false }
  }

  const [rawLat, rawLon] = value.toUpperCase().split(',')
  if (rawLat === undefined || rawLon === undefined) {
    return {
      isValid: false,
    }
  }

  const {
    decimalDegrees: lat,
    isValid: isLatValid,
    invalidReason: invalidLatReason,
  } = parseValue(rawLat.trim(), true)
  const {
    decimalDegrees: lon,
    isValid: isLonValid,
    invalidReason: invalidLonReason,
  } = parseValue(rawLon.trim(), false)

  return {
    lat,
    lon,
    isValid: isLatValid && isLonValid,
    invalidReason: invalidLatReason || invalidLonReason,
  }
}

/* eslint-disable-next-line react/display-name */
const LatLon = forwardRef(
  ({ isFocused, onFocus, onBlur, onSubmit, onReset }, ref) => {
    const [{ value, hasCoordinates, isValid, invalidReason }, setState] =
      useState({
        value: '',
        hasCoordinates: false,
        isValid: true,
        invalidReason: null,
      })

    // prevent click from calling window click handler
    const handleClick = useCallback((e) => e.stopPropagation(), [])

    const handleChange = useCallback(({ target: { value: newValue } }) => {
      const hasCoordValue = newValue.search(hasCoordsRegex) !== -1

      let nextIsValid = true
      let nextInvalidReason = null
      if (hasCoordValue) {
        const { isValid: isValueValid, invalidReason: curInvalidReason } =
          parseLatLon(newValue)
        nextIsValid = isValueValid
        nextInvalidReason = curInvalidReason
      }

      setState((prevState) => ({
        ...prevState,
        value: newValue,
        hasCoordinates: hasCoordValue,
        isValid: nextIsValid,
        invalidReason: nextInvalidReason,
      }))
    }, [])

    const handleSubmit = useCallback(() => {
      const {
        lat,
        lon,
        isValid: isValueValid,
        invalidReason: nextInvalidReason,
      } = parseLatLon(value)
      if (isValueValid) {
        onSubmit({
          latitude: lat,
          longitude: lon,
          // set a timestamp to force it to load again if user selects same
          // coords
          timestamp: new Date().getTime(),
        })
      } else {
        setState((prevState) => ({
          ...prevState,
          isValid: false,
          invalidReason: nextInvalidReason,
        }))
      }
    }, [value, onSubmit])

    const handleReset = useCallback(() => {
      setState((prevState) => ({
        ...prevState,
        value: '',
        hasCoordinates: false,
        isValid: true,
      }))

      onReset()
    }, [onReset])

    const handleInputKeyDown = useCallback(
      ({ key }) => {
        if (key === 'Enter') {
          handleSubmit()
        } else if (key === 'Escape') {
          handleReset()
        }
      },
      [handleSubmit, handleReset]
    )

    return (
      <Box
        onClick={handleClick}
        sx={{
          pr: '0.5rem',
        }}
      >
        <Flex sx={{ alignItems: 'center', gap: '0.5rem' }}>
          <Flex
            sx={{
              borderWidth: '1px',
              borderStyle: 'solid',
              borderColor: 'grey.1',
              px: '0.5rem',
              borderRadius: '0.5rem',
              color: value === '' ? 'grey.4' : 'grey.9',
              alignItems: 'center',

              ...(isValid
                ? {
                    '&:focus, &:focus-within': {
                      color: 'grey.9',
                      borderColor: 'grey.9',
                    },
                  }
                : invalidInputCSS),
            }}
          >
            <SearchLocation size="1em" style={{ flex: '0 0 auto' }} />
            <Input
              ref={ref}
              sx={{
                width: '100%',
                flex: '1 1 auto',
                border: 'none',
                outline: 'none',
                '&::placeholder': {
                  color: 'grey.4',
                },
              }}
              placeholder="Enter latitude, longitude"
              value={value}
              onClick={handleClick}
              onChange={handleChange}
              onFocus={onFocus}
              onBlur={onBlur}
              onKeyDown={handleInputKeyDown}
            />
            {value !== '' && (
              <Box
                sx={{
                  color: 'grey.5',
                  '&:hover': {
                    color: 'grey.9',
                  },
                }}
              >
                <Times
                  size="1.25em"
                  style={{
                    flex: '0 0 auto',
                    cursor: 'pointer',
                    display: 'block',
                  }}
                  onClick={handleReset}
                />
              </Box>
            )}
          </Flex>

          {isFocused ? (
            <Flex
              sx={{
                justifyContent: 'flex-end',
              }}
            >
              <Button
                disabled={!(hasCoordinates && isValid)}
                variant={hasCoordinates && isValid ? 'primary' : 'secondary'}
                onClick={handleSubmit}
                sx={{
                  fontSize: 1,
                  px: '0.75em',
                  py: '0.1em',
                  cursor: hasCoordinates && isValid ? 'pointer' : 'not-allowed',
                }}
              >
                Go
              </Button>
            </Flex>
          ) : null}
        </Flex>

        {isFocused ? (
          <>
            <Box
              className="latlon-instructions"
              sx={{
                mt: '0.5rem',
                ml: '-1rem',
                pb: '0.5rem',
                color: 'grey.8',
                fontSize: 0,
                lineHeight: 1,
              }}
            >
              Use decimal degrees or degrees° minutes&apos; seconds&quot; in
              latitude, longitude order
            </Box>

            {!isValid ? (
              <Box
                sx={{
                  mt: '0.5rem',
                  ml: '-1.5rem',
                  mr: '-1rem',
                  pb: '0.25rem',
                  lineHeight: 1,
                }}
              >
                <Flex sx={{ alignItems: 'center', gap: '0.25rem' }}>
                  <Box sx={{ color: 'accent' }}>
                    <ExclamationTriangle size="1em" />
                  </Box>
                  <Text sx={{ fontWeight: 'bold' }}>
                    The value you entered is not valid.
                  </Text>
                </Flex>
                {invalidReason ? (
                  <Text sx={{ mt: '0.25rem' }}>{invalidReason}</Text>
                ) : null}
              </Box>
            ) : null}
          </>
        ) : null}
      </Box>
    )
  }
)
LatLon.propTypes = {
  isFocused: PropTypes.bool,
  onSubmit: PropTypes.func.isRequired,
  onReset: PropTypes.func.isRequired,
  onFocus: PropTypes.func,
  onBlur: PropTypes.func,
}

LatLon.defaultProps = {
  isFocused: false,
  onFocus: () => {},
  onBlur: () => {},
}

export default LatLon
