import React, { useCallback, useState, memo, forwardRef } from 'react'
import PropTypes from 'prop-types'
import { Box, Flex } from 'theme-ui'
import { useQuery } from '@tanstack/react-query'

import { searchBarriers } from 'components/Data'

import LocationSearchField from './LocationSearchField'
import BarrierSearchResults from './BarrierSearchResults'

/* eslint-disable-next-line react/display-name */
const BarrierSearch = forwardRef(
  ({ isFocused, onSubmit, onReset, ...props }, ref) => {
    const [{ query, index, selectedId, isIdSearch }, setState] = useState({
      query: '',
      index: null,
      selectedId: null,
      isIdSearch: false,
    })

    const {
      isLoading,
      error,
      data: { results = [], remaining = 0 } = {},
    } = useQuery({
      queryKey: ['searchBarriers', query],
      queryFn: () => {
        if (!query) {
          return null
        }

        return searchBarriers(query)
      },

      enabled: !!query && query.length >= 3,
      staleTime: 60 * 60 * 1000, // 60 minutes
      // staleTime: 1, // use then reload to force refresh of underlying data during dev
      refetchOnWindowFocus: false,
      refetchOnMount: false,
    })

    // Just log the error, there isn't much we can show the user here
    if (error) {
      // eslint-disable-next-line no-console
      console.error('ERROR retrieving result from search API ', error)
    }

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
        isIdSearch: newQuery.search(/\S\S\d+/) === 0,
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

    const handleSetLocation = useCallback(
      ({ sarpid, lat: latitude, lon: longitude }) => {
        setState((prevState) => ({
          ...prevState,
          selectedId: sarpid,
        }))
        onSubmit({ latitude, longitude })
      },
      [onSubmit]
    )

    return (
      <Box onKeyDown={handleKeyDown}>
        <LocationSearchField
          ref={ref}
          value={query}
          placeholder="Find a barrier by name or ID"
          onChange={handleQueryChange}
          onReset={handleReset}
          {...props}
        />

        {isFocused && query ? (
          <>
            {query.length >= 3 ? (
              <BarrierSearchResults
                results={results}
                remaining={remaining}
                index={index}
                isLoading={isLoading}
                error={error}
                selectedId={selectedId}
                setLocation={handleSetLocation}
                showId={isIdSearch}
              />
            ) : (
              <Flex sx={{ justifyContent: 'center', color: 'grey.8' }}>
                keep typing...
              </Flex>
            )}
          </>
        ) : null}
      </Box>
    )
  }
)

BarrierSearch.propTypes = {
  isFocused: PropTypes.bool,
  onSubmit: PropTypes.func.isRequired,
  onReset: PropTypes.func.isRequired,
}

BarrierSearch.defaultProps = {
  isFocused: false,
}

export default memo(BarrierSearch)
