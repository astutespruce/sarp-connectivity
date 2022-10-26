import React, { memo, useCallback, useEffect, useState } from 'react'
import PropTypes from 'prop-types'
import { useQuery } from 'react-query'
import { Box, Text } from 'theme-ui'

import { searchUnits } from 'components/Data/API'
import { LAYER_NAMES, SYSTEMS, SYSTEM_UNITS } from 'constants'
import { formatNumber } from 'util/format'
import ListItem from './ListItem'
import SearchField from './SearchField'

const UnitSearch = ({ system, layer, onSelect }) => {
  const [query, setQuery] = useState('')

  const {
    isLoading,
    data: { results = [], meta: { remaining = 0 } = {} } = {},
  } = useQuery(
    ['search', system, layer, query],
    async () => {
      if (!(query && query.length >= 3)) {
        return {}
      }

      const layers = layer !== null ? [layer] : SYSTEM_UNITS[system]
      return searchUnits(layers, query)
    },
    {
      staleTime: 10 * 60 * 1000, // 10 minutes
      refetchOnWindowFocus: false,
      refetchOnMount: false,
    }
  )

  const showID = layer
    ? !(layer === 'State' || layer === 'County')
    : system !== 'ADM'

  const handleChange = useCallback((value) => setQuery(value), [])

  const handleSelect = (item) => () => {
    onSelect(item)
    setQuery('')
  }

  useEffect(() => {
    // reset the query
    setQuery('')
  }, [system, layer])

  const searchLabel = layer ? LAYER_NAMES[layer] : SYSTEMS[system].toLowerCase()
  const suffix = ` name${
    (system && system !== 'ADM') ||
    (layer && !(layer === 'State' || layer === 'County'))
      ? ' or ID'
      : ''
  }`

  return (
    <Box>
      <Text sx={{ fontSize: '1.25rem' }}>Search for {searchLabel}:</Text>
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
            m: 0,
            p: 0,
            listStyle: 'none',
          }}
        >
          {results.map((item) => (
            <ListItem
              key={`${item.layer}-${item.id}`}
              {...item}
              showID={showID}
              onClick={handleSelect(item)}
            />
          ))}
        </Box>
      ) : null}

      {query.length > 0 && (results.length === 0 || query.length <= 3) ? (
        <Box
          sx={{
            my: '1rem',
            textAlign: 'center',
            fontStyle: 'italic',
            color: 'grey.6',
          }}
        >
          {query.length < 3 ? '...keep typing...' : null}

          {query.length >= 3 && results.length === 0
            ? 'No results match your search'
            : null}
        </Box>
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
  system: PropTypes.string,
  layer: PropTypes.string,
  onSelect: PropTypes.func.isRequired,
}

UnitSearch.defaultProps = {
  layer: null,
  system: null,
}

export default memo(UnitSearch)
