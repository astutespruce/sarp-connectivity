import React from 'react'
import PropTypes from 'prop-types'
import { Text, View } from '@react-pdf/renderer'

import { barrierTypeLabelSingular } from 'config'
import { formatNumber } from 'util/format'

import { Bold, Flex, Link, Section } from './elements'

const SpeciesHabitat = ({
  barrierType,
  diadromoushabitat,
  habitat,
  ...props
}) => {
  const sources = [...new Set(habitat.map(({ source }) => source))]

  return (
    <Section
      title="Species habitat information for this network"
      {...props}
      wrap={false}
      marginBottom={6}
    >
      <Flex>
        <View
          style={{
            flex: '1 1 auto',
          }}
        />
        <View style={{ flex: '0 0 120pt' }}>
          <Text>
            <Bold>upstream miles</Bold>
          </Text>
        </View>
        <View style={{ flex: '0 0 120pt' }}>
          <Text>
            <Bold>downstream miles</Bold>
          </Text>
          <Text style={{ color: '#7f8a93', fontSize: 10 }}>
            free-flowing miles only
          </Text>
        </View>
      </Flex>

      {habitat.map(({ key, label, limit, upstreammiles, downstreammiles }) => (
        <Flex
          key={key}
          style={{
            borderTop: '1px solid #dee1e3',
            marginTop: 6,
            paddingTop: 6,
          }}
        >
          <View style={{ flex: '1 1 auto' }}>
            <Text>{label}</Text>
            {limit ? (
              <Text style={{ color: '#7f8a93', fontSize: 10 }}>
                Data are known to be limited to {limit}.
              </Text>
            ) : null}
          </View>
          <View style={{ flex: '0 0 120pt' }}>
            <Text>
              {upstreammiles > 0 && upstreammiles < 0.1
                ? '<0.1'
                : formatNumber(upstreammiles)}
            </Text>
          </View>
          <View style={{ flex: '0 0 120pt' }}>
            <Text>
              {downstreammiles > 0 && downstreammiles < 0.1
                ? '<0.1'
                : formatNumber(downstreammiles)}
            </Text>
          </View>
        </Flex>
      ))}

      {diadromoushabitat === 1 ? (
        <View style={{ marginTop: 24 }}>
          <Text>
            This {barrierTypeLabelSingular[barrierType]} is located on a reach
            with anadromous / catadromous species habitat.
          </Text>
        </View>
      ) : null}

      <Text style={{ color: '#7f8a93', marginTop: 28, fontSize: 10 }}>
        Note: instream habitat is estimated from data provided by regional
        partners ({sources.join(', ')}) and assigned to NHDPlusHR flowlines;
        these estimates do not fully account for elevation gradients or other
        natural barriers that may have been present in the source data. Habitat
        data are limited to available data sources and are not comprehensive and
        do not fully capture all current or potential habitat for a given
        species or group across its range. For more information, please see the{' '}
        <Link href="https://tool.aquaticbarriers.org/habitat_methods">
          analysis methods
        </Link>
        .
      </Text>
    </Section>
  )
}

SpeciesHabitat.propTypes = {
  barrierType: PropTypes.string.isRequired,
  diadromoushabitat: PropTypes.number,
  habitat: PropTypes.arrayOf(
    PropTypes.shape({
      key: PropTypes.string.isRequired,
      label: PropTypes.string.isRequired,
      source: PropTypes.string.isRequired,
      upstreammiles: PropTypes.number.isRequired,
      limit: PropTypes.string,
    })
  ).isRequired,
  sx: PropTypes.object,
}

SpeciesHabitat.defaultProps = {
  diadromoushabitat: 0,
  sx: null,
}

export default SpeciesHabitat
