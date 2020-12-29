import React, { useState } from 'react'
import PropTypes from 'prop-types'
import { FaTimesCircle, FaCaretDown, FaCaretRight } from 'react-icons/fa'

import { OutboundLink } from 'components/Link'
import { HelpText } from 'components/Text'
import { useCrossfilter } from 'components/Crossfilter'
import { Flex, Box } from 'components/Grid'
import { useIsEqualCallback, useIsEqualMemo } from 'util/hooks'

import styled, { themeGet } from 'style'
import HorizontalBars from './HorizontalBars'

const Wrapper = styled(Box).attrs({ py: '1rem' })`
  &:not(:first-child) {
    border-top: 1px solid ${themeGet('colors.grey.100')};
  }
`

const Header = styled(Flex).attrs({
  justifyContent: 'space-between',
})``

const ResetIcon = styled(FaTimesCircle).attrs({
  size: '1rem',
})`
  width: 1rem;
  height: 1rem;
  margin-left: 1rem;
  visibility: ${({ visible }) => visible};
  cursor: pointer;
  color: ${themeGet('colors.highlight.500')};
`

const CaretDown = styled(FaCaretDown)`
  width: 1.5rem;
  height: 1.5rem;
  color: ${themeGet('colors.grey.900')};
  margin-right: 0.25rem;
`

const CaretRight = styled(FaCaretRight)`
  width: 1.5rem;
  height: 1.5rem;
  color: ${themeGet('colors.grey.900')};
  margin-right: 0.25rem;
`

const Container = styled.div`
  padding: 0.5rem 0 0 1rem;
`

const EmptyMessage = styled.div`
  color: ${themeGet('colors.grey.700')};
  text-align: center;
  font-style: italic;
  font-size: smaller;
`

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
    <Wrapper>
      <Header>
        <Flex
          alignItems="flex-start"
          style={{ flex: '1 1 auto', cursor: 'pointer', fontWeight: 'bold' }}
          onClick={toggle}
        >
          {isOpen ? <CaretDown /> : <CaretRight />}
          <div>{title}</div>
        </Flex>
        <ResetIcon
          onClick={handleReset}
          visible={filterValues.size > 0 ? 'visible' : 'hidden'}
        />
      </Header>

      {isOpen && (
        <>
          {data.length > 0 && max > 0 ? (
            <Container>
              <HorizontalBars
                data={data}
                max={max}
                onToggleFilter={handleFilterToggle}
              />

              {help && (
                <HelpText fontSize="0.8rem">
                  {help}
                  {url && (
                    <>
                      <br />
                      <OutboundLink to={url} target="_blank">
                        Read more.
                      </OutboundLink>
                    </>
                  )}
                </HelpText>
              )}
            </Container>
          ) : (
            <EmptyMessage>No data available</EmptyMessage>
          )}
        </>
      )}
    </Wrapper>
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
