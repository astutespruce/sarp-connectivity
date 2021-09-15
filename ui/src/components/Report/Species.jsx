import React from 'react'
import PropTypes from 'prop-types'
import { Text, View } from '@react-pdf/renderer'

import { formatNumber } from 'util/format'

import { Bold, Flex, Section } from './elements'

const has = (num) => (num === 1 ? 'has' : 'have')

const Species = ({ tespp, statesgcnspp, regionalsgcnspp, ...props }) => {
  const colWidth = 1 / (tespp > 0) + (statesgcnspp > 0) + (regionalsgcnspp > 0)

  return (
    <Section title="Species information" {...props}>
      <Flex>
        <View
          style={{
            flex: `1 1 ${colWidth}%`,
          }}
        >
          <Text>
            <Bold>
              {formatNumber(tespp)} federally-listed threatened and endangered
              aquatic species
            </Bold>{' '}
            {has(tespp)} been found in the subwatershed containing this barrier.
          </Text>
        </View>

        <View
          style={{
            flex: `1 1 ${colWidth}%`,
            marginLeft: 14,
            paddingLeft: 14,
            borderLeft: '1px solid #cfd3d6',
          }}
        >
          <Text>
            <Bold>
              {statesgcnspp} state-listed aquatic Species of Greatest
              Conservation Need (SGCN)
            </Bold>{' '}
            {has(statesgcnspp)} been found in the subwatershed containing this
            barrier.
          </Text>
        </View>

        <View
          style={{
            flex: `1 1 ${colWidth}%`,
            marginLeft: 14,
            paddingLeft: 14,
            borderLeft: '1px solid #cfd3d6',
          }}
        >
          <Text>
            <Bold>
              {regionalsgcnspp} regionally-listed aquatic species of greatest
              conservation need
            </Bold>{' '}
            {has(regionalsgcnspp)} been identified by available data sources for
            this subwatershed.
          </Text>
        </View>
      </Flex>

      <Text style={{ color: '#7f8a93', marginTop: 28, fontSize: 10 }}>
        Note: State and regionally listed species of greatest conservation need
        may include state-listed threatened and endangered species. Species
        information is very incomplete and only includes species that have been
        identified by available data sources for this subwatershed. These
        species may or may not be directly impacted by this barrier. The absence
        of species in the available data does not necessarily indicate the
        absence of species in the subwatershed.
      </Text>
    </Section>
  )
}

Species.propTypes = {
  tespp: PropTypes.number,
  statesgcnspp: PropTypes.number,
  regionalsgcnspp: PropTypes.number,
}

Species.defaultProps = {
  tespp: 0,
  statesgcnspp: 0,
  regionalsgcnspp: 0,
}

export default Species
