import React, { memo, useCallback, useEffect, useState } from 'react'
import PropTypes from 'prop-types'
import { useQuery } from '@tanstack/react-query'
import { Box, Flex, Text } from 'theme-ui'
import { ExclamationTriangle } from '@emotion-icons/fa-solid'

import { searchUnits } from 'components/Data/API'
import { LAYER_NAMES, SYSTEMS, SYSTEM_UNITS } from 'config'
import { formatNumber } from 'util/format'
import ListItem from './ListItem'
import SearchField from './SearchField'

const UnitSearch = ({
  barrierType,
  system,
  layer,
  ignoreIds,
  showCount,
  onSelect,
}) => {
  const [{ query, activeIndex }, setState] = useState({
    query: '',
    activeIndex: null,
  })

  const {
    isLoading,
    error,
    data: { results = [], remaining = 0 } = {},
  } = useQuery({
    queryKey: ['search', system, layer, query],
    queryFn: async () => {
      if (!(query && query.length >= 3)) {
        return {}
      }

      const layers = layer !== null ? [layer] : SYSTEM_UNITS[system]

      return searchUnits(layers, query)
    },

    staleTime: 10 * 60 * 1000, // 10 minutes
    refetchOnWindowFocus: false,
    refetchOnMount: false,
  })

  const showID = layer
    ? !(layer === 'State' || layer === 'County')
    : system !== 'ADM'

  const handleChange = useCallback((value) => {
    setState(() => ({ query: value, activeIndex: null }))
  }, [])

  const handleSelect = (item) => () => {
    onSelect(item)
    setState(() => ({ query: '', activeIndex: null }))
  }

  const handleKeyDown = useCallback(
    ({ key }) => {
      // clears everything
      if (key === 'Escape') {
        setState(() => ({ query: '', activeIndex: null }))
        return
      }

      if (!(results && results.length > 0)) {
        return
      }

      if (key === 'Enter' && activeIndex !== null) {
        const item = results[activeIndex]
        if (!(ignoreIds && ignoreIds.has(item.id))) {
          onSelect(item)
        }
        setState(() => ({ query: '', activeIndex: null }))

        return
      }

      let nextIndex = 0
      if (key === 'ArrowUp' && activeIndex !== null) {
        if (activeIndex > 0) {
          nextIndex = activeIndex - 1
        } else {
          // wrap around
          nextIndex = results.length - 1
        }
        setState((prevState) => ({
          ...prevState,
          activeIndex: nextIndex,
        }))
      } else if (key === 'ArrowDown' || key === 'Tab') {
        if (activeIndex !== null) {
          if (activeIndex < results.length - 1) {
            nextIndex = activeIndex + 1
          }
          // else wrap around, handled by set = 0 above
        }
        setState((prevState) => ({
          ...prevState,
          activeIndex: nextIndex,
        }))
      }
    },
    [results, ignoreIds, activeIndex]
  )

  useEffect(() => {
    // reset the query
    setState(() => ({ query: '', activeIndex: null }))
  }, [system, layer])

  const searchLabel = layer ? LAYER_NAMES[layer] : SYSTEMS[system].toLowerCase()
  const suffix = ` name${
    (system && system !== 'ADM') ||
    (layer && !(layer === 'State' || layer === 'County'))
      ? ' or ID'
      : ''
  }`

  return (
    <Box onKeyDown={handleKeyDown}>
      <Text>Search for {searchLabel}:</Text>
      <SearchField
        value={query}
        isLoading={isLoading}
        placeholder={`${searchLabel}${suffix}`}
        onChange={handleChange}
      />

      {results.length > 0 ? (
        <Box
          as="ul"
          sx={{
            m: '2px 0 0 0',
            p: 0,
            listStyle: 'none',
          }}
        >
          {results.map((item, i) => (
            <ListItem
              key={`${item.layer}-${item.id}`}
              barrierType={barrierType}
              {...item}
              showID={showID}
              showCount={showCount}
              onClick={handleSelect(item)}
              disabled={ignoreIds && ignoreIds.has(item.id)}
              focused={i === activeIndex}
            />
          ))}
        </Box>
      ) : null}

      {query.length > 0 && (results.length === 0 || query.length <= 3) ? (
        <Flex
          sx={{
            my: '1rem',
            justifyContent: 'center',
          }}
        >
          {query.length >= 3 ? (
            <>
              {error !== null ? (
                <Flex sx={{ alignItems: 'center', gap: '0.5rem' }}>
                  <Box sx={{ color: 'highlight' }}>
                    <ExclamationTriangle size="1em" />
                  </Box>
                  <Text>Error retrieving results</Text>
                </Flex>
              ) : null}
              {error === null && !isLoading && results.length === 0 ? (
                <Text
                  sx={{
                    fontStyle: 'italic',
                    color: 'grey.6',
                  }}
                >
                  No results match your search
                </Text>
              ) : null}
            </>
          ) : (
            <Text sx={{ fontStyle: 'italic', color: 'grey.6' }}>
              ...keep typing...
            </Text>
          )}
        </Flex>
      ) : null}

      {remaining > 0 ? (
        <Box
          sx={{
            my: '1rem',
            fontSize: 1,
            textAlign: 'center',
            fontStyle: 'italic',
            color: 'grey.6',
          }}
        >
          ...and {formatNumber(remaining)} more...
        </Box>
      ) : null}
    </Box>
  )
}

UnitSearch.propTypes = {
  barrierType: PropTypes.string.isRequired,
  system: PropTypes.string,
  layer: PropTypes.string,
  ignoreIds: PropTypes.object, // Set
  showCount: PropTypes.bool,
  onSelect: PropTypes.func.isRequired,
}

UnitSearch.defaultProps = {
  layer: null,
  system: null,
  ignoreIds: null,
  showCount: false,
}

export default memo(UnitSearch)
