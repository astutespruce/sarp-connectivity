import React from 'react'
import PropTypes from 'prop-types'
import { Text, View } from '@react-pdf/renderer'

import { formatNumber, pluralize } from 'util/format'
import { Bold, Flex, Section } from './elements'

const DiadromousInfo = ({
  barrierType,
  milestooutlet,
  totaldownstreamdams,
  totaldownstreamsmallbarriers,
  totaldownstreamwaterfalls,
  ...props
}) => (
  <Section title="Diadromous species information" {...props} wrap={false}>
    <Flex>
      <View
        style={{
          flex: '1 1 25%',
        }}
      >
        <Text>
          <Bold>{formatNumber(milestooutlet)}</Bold>{' '}
          {pluralize('mile', milestooutlet)} downstream to the ocean
        </Text>
      </View>

      {totaldownstreamdams >= 0 ? (
        <View
          style={{
            flex: '1 1 25%',
            marginLeft: 14,
            paddingLeft: 14,
            borderLeft: '1px solid #cfd3d6',
          }}
        >
          <Text>
            <Bold>{formatNumber(totaldownstreamdams)}</Bold>{' '}
            {pluralize('dam', totaldownstreamdams)} downstream
          </Text>
        </View>
      ) : null}

      {barrierType === 'small_barriers' && totaldownstreamsmallbarriers >= 0 ? (
        <View
          style={{
            flex: '1 1 25%',
            marginLeft: 14,
            paddingLeft: 14,
            borderLeft: '1px solid #cfd3d6',
          }}
        >
          <Text>
            <Bold>{formatNumber(totaldownstreamsmallbarriers)}</Bold> assessed
            road-related {pluralize('barrier', totaldownstreamsmallbarriers)}{' '}
            downstream
          </Text>
        </View>
      ) : null}

      {totaldownstreamwaterfalls >= 0 ? (
        <View
          style={{
            flex: '1 1 25%',
            marginLeft: 14,
            paddingLeft: 14,
            borderLeft: '1px solid #cfd3d6',
          }}
        >
          <Text>
            <Bold>{formatNumber(totaldownstreamwaterfalls)}</Bold>{' '}
            {pluralize('waterfall', totaldownstreamwaterfalls)} downstream
          </Text>
        </View>
      ) : null}
    </Flex>
  </Section>
)

DiadromousInfo.propTypes = {
  barrierType: PropTypes.string.isRequired,
  milestooutlet: PropTypes.number,
  totaldownstreamdams: PropTypes.number,
  totaldownstreamsmallbarriers: PropTypes.number,
  totaldownstreamwaterfalls: PropTypes.number,
}

DiadromousInfo.defaultProps = {
  milestooutlet: 0,
  totaldownstreamdams: 0,
  totaldownstreamsmallbarriers: 0,
  totaldownstreamwaterfalls: 0,
}

export default DiadromousInfo
