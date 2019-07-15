import React from 'react'
import PropTypes from 'prop-types'

import { Text } from 'components/Text'
import { Flex } from 'components/Grid'
import styled, { themeGet } from 'style'

const Wrapper = styled.div`
  &:not(:first-child) {
    margin-top: 3rem;
  }
`

const Title = styled(Text).attrs({ mb: '1rem' })``

const Chart = styled(Flex).attrs({ alignItems: 'center' })``

const Label = styled.div`
  color: ${themeGet('colors.grey.700')};
  flex: 0 0 auto;
`

const Domain = styled.div`
  position: relative;
  margin: 0.25rem 1.25rem 0;
  flex: 1 1 auto;
`

const Line = styled.div`
  height: 2px;
  background: ${themeGet('colors.grey.200')};
`

const Marker = styled.div`
  position: absolute;
  padding-top: 0.25rem;
  top: -1rem;
  width: 2rem;
  height: 2rem;
  border-radius: 2rem;
  background: ${themeGet('colors.grey.800')};
  margin-left: -1rem;
  text-align: center;
  color: #fff;
`

// All scores are normalized on a 0-1 basis, with 0 being lowest value
const ScoreChart = ({ label, score, tier }) => (
  <Wrapper>
    <Title>{label}</Title>
    <Chart>
      <Label>Low</Label>
      <Domain>
        <Line />
        <Marker style={{ left: `${score}%` }}>{tier}</Marker>
      </Domain>
      <Label>High</Label>
    </Chart>
  </Wrapper>
)

ScoreChart.propTypes = {
  label: PropTypes.string.isRequired,
  score: PropTypes.number.isRequired,
  tier: PropTypes.number.isRequired,
}

export default ScoreChart
