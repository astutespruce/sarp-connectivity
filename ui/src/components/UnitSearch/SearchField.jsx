import React, { useCallback, useEffect, useState } from 'react'
import PropTypes from 'prop-types'
import { useDebouncedCallback } from 'use-debounce'
import { Input, Flex, Box, Spinner } from 'theme-ui'
import { TimesCircle } from '@emotion-icons/fa-solid'

const SearchField = ({ value, placeholder, isLoading, onChange }) => {
  const [query, setQuery] = useState('')

  const debouncedOnChange = useDebouncedCallback((newValue) => {
    onChange(newValue)
  }, 200)

  const handleChange = useCallback(
    ({ target: { value: newValue } }) => {
      setQuery(() => newValue)
      debouncedOnChange(newValue)
    },
    [debouncedOnChange]
  )

  const handleClick = useCallback(() => {
    onChange(query)
  }, [query, onChange])

  const handleReset = useCallback(() => {
    setQuery(() => '')
    onChange('')
  }, [onChange])

  // reset the field
  useEffect(() => {
    if (value === '') {
      setQuery('')
    }
  }, [value])

  return (
    <Flex
      sx={{
        position: 'relative',
        zIndex: 2,
        alignItems: 'center',
        bg: '#FFF',
        border: '1px solid',
        borderColor: 'grey.2',
        px: '0.5rem',
        borderRadius: '0.5rem',
        color: query === '' ? 'grey.4' : 'grey.9',
        '&:focus, &:focus-within': {
          color: 'grey.9',
          borderColor: 'grey.9',
        },
      }}
    >
      <Input
        autoFocus
        sx={{
          width: '100%',
          flex: '1 1 auto',
          border: 'none',
          outline: 'none',
          '&::placeholder': {
            color: 'grey.4',
          },
        }}
        value={query}
        placeholder={placeholder}
        onChange={handleChange}
        onClick={handleClick}
      />

      <Box
        sx={{
          flex: '0 0 auto',
          color: 'grey.5',
          '&:hover': {
            color: 'grey.9',
          },
        }}
      >
        {isLoading ? <Spinner size="1.25em" sx={{ lineHeight: 1 }} /> : null}

        {!isLoading && query !== '' ? (
          <TimesCircle
            size="1.25em"
            style={{
              cursor: 'pointer',
            }}
            onClick={handleReset}
          />
        ) : null}
      </Box>
    </Flex>
  )
}

SearchField.propTypes = {
  value: PropTypes.string,
  placeholder: PropTypes.string.isRequired,
  isLoading: PropTypes.bool,
  onChange: PropTypes.func.isRequired,
}

SearchField.defaultProps = {
  value: '',
  isLoading: false,
}

export default SearchField
