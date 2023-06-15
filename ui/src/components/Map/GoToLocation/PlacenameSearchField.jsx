import React, {
  useEffect,
  useState,
  useCallback,
  useRef,
  forwardRef,
} from 'react'
import PropTypes from 'prop-types'
import { Search, Times } from '@emotion-icons/fa-solid'
import { Box, Flex, Input } from 'theme-ui'

/* eslint-disable-next-line react/display-name */
const PlacenameSearchField = forwardRef(
  ({ value, onChange, onReset, onFocus, onBlur }, ref) => {
    const [internalValue, setInternalValue] = useState('')
    const timeoutRef = useRef(null)

    // prevent click from calling window click handler
    const handleClick = useCallback((e) => e.stopPropagation(), [])

    const handleChange = useCallback(
      ({ target: { value: newValue } }) => {
        setInternalValue(() => newValue)

        // debounce call to onChange
        if (timeoutRef.current !== null) {
          clearTimeout(timeoutRef.current)
        }
        timeoutRef.current = setTimeout(() => {
          onChange(newValue)
          clearTimeout(timeoutRef.current)
        }, 250)
      },
      [onChange]
    )

    const handleReset = useCallback(() => {
      setInternalValue(() => '')
      onReset()
    }, [onReset])

    useEffect(() => {
      // set value on mount if context has a previous value
      setInternalValue(value)
    }, [value])

    return (
      <Box className="search-field-container">
        <Flex
          className="search-field"
          sx={{
            border: '1px solid',
            borderColor: 'grey.1',
            px: '0.5rem',
            borderRadius: '0.5rem',
            color: value === '' ? 'grey.4' : 'grey.9',
            alignItems: 'center',
            '&:focus, &:focus-within': {
              color: 'grey.9',
              borderColor: 'grey.9',
            },
          }}
        >
          <Search size="1em" style={{ flex: '0 0 auto' }} />
          <Input
            ref={ref}
            sx={{
              width: '100%',
              flex: '1 1 auto',
              border: 'none',
              outline: 'none',
              fontSize: 1,
              p: '0.3rem',
              '&::placeholder': {
                color: 'grey.4',
              },
            }}
            placeholder="Find a place by name / address"
            value={internalValue}
            onClick={handleClick}
            onChange={handleChange}
            onFocus={onFocus}
            onBlur={onBlur}
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
      </Box>
    )
  }
)

PlacenameSearchField.propTypes = {
  value: PropTypes.string,
  onChange: PropTypes.func.isRequired,
  onReset: PropTypes.func.isRequired,
  onFocus: PropTypes.func,
  onBlur: PropTypes.func,
}

PlacenameSearchField.defaultProps = {
  value: '',
  onFocus: () => {},
  onBlur: () => {},
}

export default PlacenameSearchField
