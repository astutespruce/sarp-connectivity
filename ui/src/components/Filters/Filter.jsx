import React, { useState } from 'react'
import PropTypes from 'prop-types'
import { TimesCircle, CaretDown, CaretRight } from '@emotion-icons/fa-solid'
import { Box, Flex, Text } from 'theme-ui'

import { OutboundLink } from 'components/Link'
import { useCrossfilter } from 'components/Crossfilter'
import { useIsEqualCallback, useIsEqualMemo } from 'util/hooks'

import HorizontalBars from './HorizontalBars'

const Filter = ({
  field,
  title,
  values,
  labels,
  help,
  url,
  isOpen: initIsOpen,
  hideEmpty,
  sort,
}) => {
  const [isOpen, setIsOpen] = useState(initIsOpen)
  const {
    setFilter,
    state: { filters, dimensionCounts },
  } = useCrossfilter()

  const filterValues = filters[field] || new Set()
  const counts = dimensionCounts[field] || {}
  const max = Math.max(0, ...Object.values(counts))

  // Memoize processing of data, since the context changes frequently
  // but the data that impact this filter may not change as frequently

  const data = useIsEqualMemo(() => {
    // if not isOpen, we can bypass processing the data
    if (!isOpen) {
      return []
    }

    // splice together label, value, and count so that we can filter and sort
    let newData = values.map((value, i) => ({
      value,
      label: labels ? labels[i] : value,
      quantity: counts[value] || 0,
      isFiltered: filterValues.has(value),
      isExcluded: filterValues.size > 0 && !filterValues.has(value),
    }))

    if (hideEmpty) {
      newData = newData.filter(
        ({ quantity, isFiltered }) => quantity > 0 || isFiltered
      )
    }

    if (sort) {
      newData = newData.sort((a, b) => {
        if (a.quantity === b.quantity) {
          return a.label < b.label ? -1 : 1
        }
        return a.quantity < b.quantity ? 1 : -1
      })
    }
    return newData
  }, [filterValues, counts, isOpen])

  const toggle = () => {
    setIsOpen((prev) => !prev)
  }

  const handleFilterToggle = useIsEqualCallback(
    (value) => {
      // NOTE: do not mutate filter values or things break
      // (not seen as a state update and memoized function above doesn't fire)!
      // Copy instead.
      const newFilterValues = new Set(filterValues)

      if (newFilterValues.has(value)) {
        newFilterValues.delete(value)
      } else {
        newFilterValues.add(value)
      }

      setFilter(field, newFilterValues)
    },
    [filterValues]
  )

  const handleReset = () => {
    setFilter(field, new Set())
  }

  return (
    <Box
      sx={{
        py: '1rem',
        '&:not(:first-of-type)': {
          borderTop: '1px solid',
          borderTopColor: 'grey.1',
        },
      }}
    >
      <Flex sx={{ justifyContent: 'space-between' }}>
        <Flex
          sx={{
            justifyContent: 'flex-start',
            flex: '1 1 auto',
            cursor: 'pointer',
            fontWeight: 'bold',
          }}
          onClick={toggle}
        >
          {isOpen ? <CaretDown size="1.5em" /> : <CaretRight size="1.5em" />}
          <Text sx={{ ml: '0.25rem' }}>{title}</Text>
        </Flex>
        <Box
          onClick={handleReset}
          sx={{
            flex: '0 0 auto',
            cursor: 'pointer',
            ml: '1rem',
            color: 'highlight',
            visibility: filterValues.size > 0 ? 'visible' : 'hidden',
          }}
        >
          <TimesCircle size="1em" />
        </Box>
      </Flex>

      {isOpen && (
        <>
          {data.length > 0 && max > 0 ? (
            <Box sx={{ pt: '0.5rem', pl: '1rem' }}>
              <HorizontalBars
                data={data}
                max={max}
                onToggleFilter={handleFilterToggle}
              />

              {help && (
                <Text variant="help" sx={{ fontSize: 0 }}>
                  {help}
                  {url && (
                    <>
                      <br />
                      <OutboundLink to={url}>Read more.</OutboundLink>
                    </>
                  )}
                </Text>
              )}
            </Box>
          ) : (
            <Text
              sx={{
                color: 'grey.7',
                fontStyle: 'italic',
                fontSize: 1,
                textAlign: 'center',
              }}
            >
              No data available
            </Text>
          )}
        </>
      )}
    </Box>
  )
}

Filter.propTypes = {
  field: PropTypes.string.isRequired,
  title: PropTypes.string.isRequired,
  values: PropTypes.array.isRequired,
  labels: PropTypes.array,
  help: PropTypes.string,
  url: PropTypes.string,
  isOpen: PropTypes.bool,
  hideEmpty: PropTypes.bool,
  sort: PropTypes.bool,
}

Filter.defaultProps = {
  labels: null,
  help: null,
  url: null,
  isOpen: false,
  hideEmpty: false,
  sort: false,
}

export default Filter
