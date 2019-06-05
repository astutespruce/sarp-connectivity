import React, { useContext } from 'react'
import PropTypes from 'prop-types'
import { FaRegTimesCircle } from 'react-icons/fa'
import { Text } from 'rebass'

import { Context as Crossfilter, RESET_FILTERS } from 'components/Crossfilter'
import { Button } from 'components/Button'
import { Flex, Box, Columns, Column } from 'components/Grid'
import { formatNumber } from 'util/format'
import styled, { themeGet } from 'style'
import Filter from './Filter'

const Wrapper = styled(Flex).attrs({
  flexDirection: 'column',
  flex: 1,
})``

const Header = styled(Columns).attrs({
  flex: 0,
  px: '1rem',
  pb: '0.5rem',
})`
  border-bottom: 1px solid ${themeGet('colors.grey.200')};
`

export const Count = styled.div`
  color: ${themeGet('colors.grey.600')};
  font-size: 0.8em;
  line-height: 1.2;
`

const ResetButton = styled(Button).attrs({ secondary: true })`
  font-size: 0.8rem;
  padding: 0.1rem 0.5rem;
`

const ResetButtonContents = styled(Flex).attrs({
  alignItems: 'center',
  justifyContent: 'flex-end',
})``

const ResetIcon = styled(FaRegTimesCircle).attrs({
  size: '1em',
})`
  margin-right: 0.25rem;
  cursor: pointer;
`

const Filters = styled(Box).attrs({ flex: 1, pr: '1rem' })`
  overflow-y: auto;
`

const FiltersList = ({ filters }) => {
  const { state, dispatch } = useContext(Crossfilter)

  const hasFilters =
    filters.filter(({ field }) => {
      const curFilter = state.get('filters').get(field)
      return curFilter && !curFilter.isEmpty()
    }).length > 0

  const handleReset = () => {
    dispatch({
      type: RESET_FILTERS,
      payload: {
        fields: filters.map(({ field }) => field),
      },
    })
  }

  let valueField = state.get('valueField')
  // TODO: generalize
  if (valueField === 'id') {
    valueField = 'detectors'
  }

  const filteredTotal = state.get('filteredTotal')
  const total = state.get('total')

  return (
    <Wrapper>
      <Header alignItems="baseline">
        <Column>
          <Count>
            {formatNumber(filteredTotal, 0)}{' '}
            {filteredTotal < total ? `of ${formatNumber(total, 0)}` : ''}{' '}
            {valueField} currently visible
          </Count>
        </Column>
        <Column flex="0 0 auto">
          {hasFilters && (
            <Text textAlign="right">
              <ResetButton onClick={handleReset}>
                <ResetButtonContents>
                  <ResetIcon />
                  <div>reset all filters</div>
                </ResetButtonContents>
              </ResetButton>
            </Text>
          )}
        </Column>
      </Header>

      <Filters>
        {filters.map(filter => (
          <Filter key={filter.field} {...filter} />
        ))}
      </Filters>
    </Wrapper>
  )
}

FiltersList.propTypes = {
  filters: PropTypes.arrayOf(
    PropTypes.shape({
      field: PropTypes.string.isRequired,
      filterFunc: PropTypes.func.isRequired,
      title: PropTypes.string.isRequired,
      values: PropTypes.arrayOf(
        PropTypes.oneOfType([PropTypes.string, PropTypes.number])
      ),
      labels: PropTypes.arrayOf(PropTypes.string),
    })
  ).isRequired,
}

export default FiltersList
