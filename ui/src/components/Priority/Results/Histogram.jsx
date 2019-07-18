/* eslint-disable react/no-array-index-key */
import React from 'react'
import PropTypes from 'prop-types'

import { Flex } from 'components/Grid'
import styled, { css, themeGet } from 'style'

import { formatNumber } from 'util/format'

const Wrapper = styled.div`
  flex: 1 1 auto;
  padding: 0.25rem 0;
`

const Label = styled.div`
  width: 4em;
  color: ${themeGet('colors.grey.700')};
  font-size: 0.8rem;
`

const AxisLabel = styled(Label)`
  text-align: right;
  margin-right: 0.25em;
`

const Count = styled(Label)`
  margin-left: 0.25em;
`

const BarContainer = styled(Flex).attrs({ alignItems: 'center' })`
  flex: 1 1 auto;
  margin-right: 0.25rem;
  padding: 0.1em 0;
  border-left: 1px solid #aaa;
`

const Bar = styled.div`
  height: 1rem;
  background-color: ${themeGet('colors.primary.500')};
`

const Row = styled(Flex).attrs({ alignItems: 'center', mb: '0.25rem' })`
  ${({ isActive }) =>
    isActive &&
    css`
      ${Label} {
        color: ${themeGet('colors.accent.500')};
      }

      ${Bar} {
        background-color: ${themeGet('colors.accent.500')};
      }
    `}
`

const Histogram = ({ counts, threshold }) => {
  const max = Math.max(...counts)

  const labelWidth = max.toString().length * 0.75

  return (
    <Wrapper>
      {counts.map((count, i) => (
        <Row key={`${i}-${count}`} isActive={i + 1 <= threshold}>
          <AxisLabel>Tier {i + 1}</AxisLabel>
          <BarContainer>
            <Bar
              style={{
                width: `calc(${(100 * count) / max}% - ${labelWidth}em)`,
              }}
            />
            <Count>{formatNumber(count, 0)}</Count>
          </BarContainer>
        </Row>
      ))}
    </Wrapper>
  )
}

Histogram.propTypes = {
  counts: PropTypes.arrayOf(PropTypes.number).isRequired,
  threshold: PropTypes.number.isRequired,
}

export default Histogram
