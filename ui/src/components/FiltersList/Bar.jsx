import React, { memo } from 'react'
import PropTypes from 'prop-types'

import { Flex, Columns, Column } from 'components/Grid'
import styled, { themeGet } from 'style'
import { formatNumber } from 'util/format'

const Wrapper = styled.div`
  cursor: pointer;
  line-height: 1;
  margin-bottom: 1rem;

  transition: opacity 300ms;
  opacity: ${({ isExcluded }) => (isExcluded ? 0.25 : 1)};

  &:hover {
    opacity: ${({ isExcluded }) => (isExcluded ? 0.5 : 1)};
  }
`

const Labels = styled(Columns).attrs({
  justifyContent: 'space-between',
})`
  color: ${({ active }) =>
    active ? themeGet('colors.highlight.500') : themeGet('colors.grey.700')};
  font-size: 0.8rem;
`

const IndicatorWrapper = styled(Flex).attrs({
  flexWrap: 'nowrap',
})`
  height: 0.5rem;
  border-radius: 0.25rem;
  background-color: ${themeGet('colors.grey.200')};
  border: 1px solid ${themeGet('colors.grey.200')};
  overflow: hidden;
`

const Indicator = styled.div`
  background-color: ${themeGet('colors.primary.500')};
  flex-grow: ${({ width }) => width};
  transition: flex-grow 300ms;
`

const FilteredIndicator = styled(Indicator)`
  background-color: ${themeGet('colors.highlight.500')};
`

const Filler = styled.div`
  transition: flex-grow 300ms;
`

const Bar = ({ isFiltered, isExcluded, label, quantity, max, onClick }) => {
  const position = quantity / max
  const remainder = 1 - position

  return (
    <Wrapper onClick={onClick} isExcluded={isExcluded}>
      <Labels active={isFiltered}>
        <Column>{label}</Column>
        <Column flex={0}>{formatNumber(quantity)}</Column>
      </Labels>
      <IndicatorWrapper>
        {position > 0 && (
          <>
            {isFiltered ? (
              <FilteredIndicator style={{ flexGrow: position }} />
            ) : (
              <Indicator style={{ flexGrow: position }} />
            )}
          </>
        )}

        {remainder > 0 && <Filler style={{ flexGrow: remainder }} />}
      </IndicatorWrapper>
    </Wrapper>
  )
}

Bar.propTypes = {
  isFiltered: PropTypes.bool, // true if filter is set on this bar
  isExcluded: PropTypes.bool, // true if filters are set on others but not this one
  label: PropTypes.oneOfType([PropTypes.string, PropTypes.number]).isRequired,
  quantity: PropTypes.number.isRequired,
  max: PropTypes.number.isRequired,
  onClick: PropTypes.func.isRequired,
}

Bar.defaultProps = {
  isFiltered: false,
  isExcluded: false,
}

// TODO: optimize for changes to the callback
export default memo(Bar)
