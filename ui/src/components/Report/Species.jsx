import React from 'react'
import PropTypes from 'prop-types'
import { Text, View } from '@react-pdf/renderer'

import { formatNumber } from 'util/format'

import { Bold, Flex, Section } from './elements'

const Species = ({
  barrierType,
  tespp,
  statesgcnspp,
  regionalsgcnspp,
  trout,
  ...props
}) => (
  <Section title="Species information" {...props}>
    <View>
      <Text>
        Data sources in the subwatershed containing this{' '}
        {barrierType === 'dams' ? 'dam' : 'road-related barrier'} have recorded:
      </Text>
    </View>

    <Flex style={{ marginTop: 24 }}>
      <View
        style={{
          flex: '1 1 25%',
        }}
      >
        <Text>
          <Bold>{formatNumber(tespp)}</Bold> federally-listed threatened and
          endangered aquatic species
        </Text>
      </View>

      <View
        style={{
          flex: '1 1 25%',
          marginLeft: 14,
          paddingLeft: 14,
          borderLeft: '1px solid #cfd3d6',
        }}
      >
        <Text>
          <Bold>{statesgcnspp}</Bold> state-listed aquatic Species of Greatest
          Conservation Need (SGCN)
        </Text>
      </View>

      <View
        style={{
          flex: '1 1 25%',
          marginLeft: 14,
          paddingLeft: 14,
          borderLeft: '1px solid #cfd3d6',
        }}
      >
        <Text>
          <Bold>{regionalsgcnspp}</Bold> regionally-listed aquatic Species of
          Greatest Conservation Need
        </Text>
      </View>
      <View
        style={{
          flex: '1 1 25%',
          marginLeft: 14,
          paddingLeft: 14,
          borderLeft: '1px solid #cfd3d6',
        }}
      >
        <Text>{trout ? 'One or more trout species' : 'No trout species'}</Text>
      </View>
    </Flex>

    <Text style={{ color: '#7f8a93', marginTop: 24, fontSize: 10 }}>
      Note: State and regionally listed species of greatest conservation need
      may include state-listed threatened and endangered species. Species
      information is very incomplete and only includes species that have been
      identified by available data sources for this subwatershed. These species
      may or may not be directly impacted by this barrier. The absence of
      species in the available data does not necessarily indicate the absence of
      species in the subwatershed.
    </Text>
  </Section>
)

Species.propTypes = {
  barrierType: PropTypes.string.isRequired,
  tespp: PropTypes.number,
  statesgcnspp: PropTypes.number,
  regionalsgcnspp: PropTypes.number,
  trout: PropTypes.number,
}

Species.defaultProps = {
  tespp: 0,
  statesgcnspp: 0,
  regionalsgcnspp: 0,
  trout: false,
}

export default Species
