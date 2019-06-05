import React, { useState, useContext } from 'react'
import PropTypes from 'prop-types'
import { Map, Set } from 'immutable'
import { FaRegTimesCircle, FaCaretDown, FaCaretRight } from 'react-icons/fa'

import { HelpText } from 'components/Text'
import { Context as Crossfilter, SET_FILTER } from 'components/Crossfilter'
import { Flex } from 'components/Grid'

import styled, { theme, themeGet } from 'style'
import Bar from './Bar'

const Wrapper = styled.div`
  padding-top: 0.25rem;

  &:not(:first-child) {
    border-top: 1px solid ${themeGet('colors.grey.200')};
  }
`

const Header = styled(Flex).attrs({
  justifyContent: 'space-between',
})``

const Title = styled(Flex).attrs({ alignItems: 'center', flex: 1 })`
  cursor: pointer;
`

const ResetIcon = styled(FaRegTimesCircle).attrs({
  size: '1rem',
})`
  width: 1rem;
  height: 1rem;
  margin-left: 1rem;
  visibility: ${({ visible }) => visible};
  cursor: pointer;
  color: ${themeGet('colors.highlight.500')};
`

const expandoColor = theme.colors.grey[800]
const expandoSize = '1.5rem'

const CaretDown = styled(FaCaretDown).attrs({
  color: expandoColor,
  size: expandoSize,
})`
  width: 1rem;
  height: 1rem;
  margin-right: 0.25rem;
`

const CaretRight = styled(FaCaretRight).attrs({
  color: expandoColor,
  size: expandoSize,
})`
  width: 1rem;
  height: 1rem;
  margin-right: 0.25rem;
`

const Bars = styled.div`
  padding: 0.5rem 0 0 1rem;
`

const EmptyMessage = styled.div`
  color: ${themeGet('colors.grey.600')};
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
  isOpen: initIsOpen,
  hideEmpty,
  sort,
}) => {
  const [isOpen, setIsOpen] = useState(initIsOpen)
  const { state, dispatch } = useContext(Crossfilter)

  const filterValues = state.get('filters').get(field, Set())
  const totals = state.get('dimensionTotals').get(field, Map())
  const max = totals.max()

  // splice together label, value, and count so that we can filter and sort
  let data = values.map((value, i) => ({
    value,
    label: labels ? labels[i] : value,
    quantity: totals.get(value, 0),
    isFiltered: filterValues.has(value),
    isExcluded: !filterValues.isEmpty() && !filterValues.has(value),
  }))

  if (hideEmpty) {
    data = data.filter(({ quantity, isFiltered }) => quantity > 0 || isFiltered)
  }

  if (sort) {
    data = data.sort((a, b) => (a.quantity < b.quantity ? 1 : -1))
  }

  const toggle = () => {
    setIsOpen(prev => !prev)
  }

  const handleFilterClick = value => {
    dispatch({
      type: SET_FILTER,
      payload: {
        field,
        // TODO: adapt to other types
        filterValue: filterValues.has(value)
          ? filterValues.delete(value)
          : filterValues.add(value),
      },
    })
  }

  const handleReset = () => {
    dispatch({
      type: SET_FILTER,
      payload: {
        field,
        filterValue: filterValues.clear(),
      },
    })
  }

  return (
    <Wrapper>
      <Header>
        <Title onClick={toggle}>
          {isOpen ? <CaretDown /> : <CaretRight />}
          <div>{title}</div>
        </Title>
        {
          <ResetIcon
            onClick={handleReset}
            visible={filterValues.size > 0 ? 'visible' : 'hidden'}
          />
        }
      </Header>

      {isOpen && (
        <>
          {data.length > 0 ? (
            <Bars>
              {data.map(({ value, ...props }) => (
                <Bar
                  key={value}
                  value={value}
                  {...props}
                  max={max}
                  onClick={() => handleFilterClick(value)}
                />
              ))}

              {help && <HelpText>{help}</HelpText>}
            </Bars>
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
  isOpen: PropTypes.bool,
  hideEmpty: PropTypes.bool,
  sort: PropTypes.bool,
}

Filter.defaultProps = {
  labels: null,
  help: null,
  isOpen: false,
  hideEmpty: false,
  sort: false,
}

export default Filter
