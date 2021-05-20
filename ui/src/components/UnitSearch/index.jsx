import React, { memo, useState } from 'react'
import PropTypes from 'prop-types'
import { Box, Heading, Flex, Input, Text } from 'theme-ui'

import { useBoundsData } from 'components/Data'
import ListItem from './ListItem'
import { LAYER_NAMES, SYSTEMS, SYSTEM_UNITS } from '../../../config/constants'

// const Wrapper = styled(Box)``

// const Header = styled(Text)`
//   font-size: 1.25rem;
// `

// const Input = styled.input.attrs({
//   type: 'text',
// })`
//   width: 100%;
//   border: 1px solid ${themeGet('colors.grey.500')};
//   border-radius: 0.25rem;
//   outline: none;
//   padding: 0.25rem 0.5rem;

//   &:focus {
//     border-color: ${themeGet('colors.primary.500')};
//   }
// `

// const List = styled.ul`
//   list-style: none;
//   margin: 0;
// `

// const NoResults = styled(Box).attrs({ my: '1rem' })`
//   text-align: center;
//   font-style: italic;
//   color: ${themeGet('colors.grey.600')};
// `

const UnitSearch = ({ system, layer, onSelect }) => {
  const data = useBoundsData()
  const [query, setQuery] = useState('')

  const showID = layer
    ? !(layer === 'State' || layer === 'County')
    : system !== 'ADM'

  const handleChange = ({ target: { value } }) => {
    setQuery(value)
  }

  const handleSelect = (item) => () => {
    onSelect(item)
    setQuery('')
  }

  let results = []
  if (query && query !== '') {
    let units = []
    if (layer !== null) {
      units = data[layer]
    } else {
      // search all layers within system
      units = SYSTEM_UNITS[system].reduce(
        (collector, systemLayer) => collector.concat(data[systemLayer]),
        []
      )
    }
    // Filter out the top 10
    try {
      // strip all special regex characters first, we don't need them here
      const expr = new RegExp(query.replace(/[.*+?^${}()|[\]\\]/g, ''), 'gi')
      const filtered = units.filter(
        ({ name, id }) =>
          name.search(expr) !== -1 || (showID && id.search(expr) !== -1)
      )
      results = filtered.slice(0, 10)
    } catch (ex) {
      console.error(ex)
    }
  }

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
      <Input
        type="text"
        variant="input-default"
        placeholder={`${searchLabel}${suffix}`}
        value={query}
        onChange={handleChange}
      />
      {query !== '' && (
        <>
          {results.length > 0 ? (
            <Box
              as="ul"
              sx={{
                m: '0 0 2rem 0',
                p: 0,
                listStyle: 'none',
              }}
            >
              {results.map((item) => (
                <ListItem
                  key={item.id}
                  {...item}
                  showID={showID}
                  onClick={handleSelect(item)}
                />
              ))}
            </Box>
          ) : (
            <Box
              sx={{
                my: '1rem',
                textAlign: 'center',
                fontStyle: 'italic',
                color: 'grey.6',
              }}
            >
              No results match your search
            </Box>
          )}
        </>
      )}
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
