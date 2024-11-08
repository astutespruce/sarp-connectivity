import React, { useState, useCallback } from 'react'
import PropTypes from 'prop-types'
import { TimesCircle, CaretDown, CaretRight } from '@emotion-icons/fa-solid'
import { Box, Flex, Text } from 'theme-ui'

import { useCrossfilter } from 'components/Crossfilter'
import { reduceToObject } from 'util/data'
import { pluralize } from 'util/format'
import Filter from './Filter'

const FilterGroup = ({ id, title, filters }) => {
  const [isOpen, setIsOpen] = useState(false)

  // all filters initially closed
  const [openFilters, setOpenFilters] = useState(() =>
    filters.reduce(...reduceToObject('field', () => false))
  )

  const {
    resetGroupFilters,
    state: { filters: filterState, emptyDimensions },
  } = useCrossfilter()

  const toggle = () => {
    setIsOpen((prev) => !prev)
  }

  const handleFilterToggle = useCallback(
    (field) => () => {
      setOpenFilters((prevState) => ({
        ...prevState,
        [field]: !prevState[field],
      }))
    },
    []
  )

  const handleReset = () => {
    resetGroupFilters(id)
  }

  const hasFilters =
    filters.filter(
      ({ field }) => filterState[field] && filterState[field].size > 0
    ).length > 0

  const availableFilters = filters.filter(
    ({ field, hideIfEmpty }) => !(hideIfEmpty && emptyDimensions.has(field))
  )

  if (availableFilters.length === 0) {
    return null
  }

  return (
    <Box
      sx={{
        mr: '-1rem',
        ml: '-1rem',
        '&:not(:first-of-type)': {
          pt: '0.5rem',
        },
        borderBottom: '2px solid',
        borderBottomColor: 'grey.2',
      }}
    >
      <Flex
        sx={{
          justifyContent: 'space-between',
          bg: 'grey.1',
          py: '0.5rem',
          pl: '0.15rem',
          pr: '1rem',
        }}
      >
        <Flex
          sx={{
            justifyContent: 'flex-start',
            flex: '1 1 auto',
            cursor: 'pointer',
          }}
          onClick={toggle}
        >
          {isOpen ? <CaretDown size="1.5em" /> : <CaretRight size="1.5em" />}
          <Box sx={{ ml: '0.25rem' }}>
            <Text sx={{ fontWeight: 'bold' }}>{title}</Text>
            <Text sx={{ fontSize: 0, color: 'grey.7' }}>
              {availableFilters.length}{' '}
              {pluralize('filter', availableFilters.length)} available
            </Text>
          </Box>
        </Flex>
        <Box
          onClick={handleReset}
          sx={{
            flex: '0 0 auto',
            cursor: 'pointer',
            ml: '1rem',
            color: 'highlight',
            visibility: hasFilters ? 'visible' : 'hidden',
          }}
          title={`Reset all filters in ${title.toLowerCase()}`}
        >
          <TimesCircle size="1em" />
        </Box>
      </Flex>

      {isOpen ? (
        <Box
          sx={{
            pl: '0.25rem',
            pr: '1rem',
            borderLeft: '0.5rem solid',
            borderLeftColor: 'grey.1',
          }}
        >
          {availableFilters.map((filter) => (
            <Filter
              key={filter.field}
              {...filter}
              isOpen={openFilters[filter.field]}
              onToggle={handleFilterToggle(filter.field)}
            />
          ))}
        </Box>
      ) : null}
    </Box>
  )
}

FilterGroup.propTypes = {
  id: PropTypes.string.isRequired,
  title: PropTypes.string.isRequired,
  filters: PropTypes.arrayOf(PropTypes.shape(Filter.propTypes)).isRequired,
}

export default FilterGroup
