import React, { useCallback, useState, memo, forwardRef } from 'react'
import PropTypes from 'prop-types'
import { Box } from 'theme-ui'

import { useIsEqualEffect } from 'util/hooks'
import { useMapboxSearch } from './mapbox'
import Results from './Results'
import PlacenameSearchField from './PlacenameSearchField'

/* eslint-disable-next-line react/display-name */
const PlacenameSearch = forwardRef(
  ({ isFocused, onSubmit, onReset, ...props }, ref) => {
    const [{ query, index, selectedId }, setState] = useState({
      query: '',
      index: null,
      selectedId: null,
    })

    const { results, location, isLoading, error } = useMapboxSearch(
      query,
      selectedId
    )

    useIsEqualEffect(() => {
      if (location !== null) {
        onSubmit(location)
      }
    }, [location])

    const handleKeyDown = useCallback(
      ({ key }) => {
        if (!(results && results.length > 0)) {
          return
        }

        let nextIndex = 0
        if (key === 'ArrowUp' && index !== null) {
          if (index > 0) {
            nextIndex = index - 1
          } else {
            // wrap around
            nextIndex = results.length - 1
          }
          setState((prevState) => ({ ...prevState, index: nextIndex }))
        } else if (key === 'ArrowDown') {
          if (index !== null) {
            if (index < results.length - 1) {
              nextIndex = index + 1
            }
            // else wrap around, handled by set = 0 above
          }
          setState((prevState) => ({ ...prevState, index: nextIndex }))
        }
      },
      [results, index]
    )

    const handleQueryChange = useCallback((newQuery) => {
      setState((prevState) => ({
        ...prevState,
        query: newQuery,
        results: null,
        selectedId: null,
        index: null,
      }))
    }, [])

    const handleReset = useCallback(() => {
      setState((prevState) => ({
        ...prevState,
        query: '',
        results: null,
        selectedId: null,
        index: null,
      }))
      onReset()
    }, [onReset])

    const handleSelectId = useCallback((id) => {
      setState((prevState) => ({
        ...prevState,
        selectedId: id,
      }))
    }, [])

    return (
      <Box onKeyDown={handleKeyDown}>
        <PlacenameSearchField
          ref={ref}
          value={query}
          onChange={handleQueryChange}
          onReset={handleReset}
          {...props}
        />

        {isFocused && query && query.length >= 3 ? (
          <Results
            results={results}
            index={index}
            isLoading={isLoading}
            error={error}
            selectedId={selectedId}
            setSelectedId={handleSelectId}
          />
        ) : null}
      </Box>
    )
  }
)

PlacenameSearch.propTypes = {
  isFocused: PropTypes.bool,
  onSubmit: PropTypes.func.isRequired,
  onReset: PropTypes.func.isRequired,
}

PlacenameSearch.defaultProps = {
  isFocused: false,
}

export default memo(PlacenameSearch)
