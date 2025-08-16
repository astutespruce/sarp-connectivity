/* eslint-disable camelcase */
import React from 'react'
import PropTypes from 'prop-types'
import { Text, View } from '@react-pdf/renderer'

import { barrierTypeLabels, STATES } from 'config'
import { Bold, Flex, Italic, Section } from './elements'

const Scores = ({
  barrierType,
  networkType,
  state,
  ranked,
  invasive,
  state_nc_tier,
  state_wc_tier,
  state_ncwc_tier,
  state_pnc_tier,
  state_pwc_tier,
  state_pncwc_tier,
  state_mnc_tier,
  state_mwc_tier,
  state_mncwc_tier,
  huc8_nc_tier,
  huc8_wc_tier,
  huc8_ncwc_tier,
  huc8_pnc_tier,
  huc8_pwc_tier,
  huc8_pncwc_tier,
  huc8_mnc_tier,
  huc8_mwc_tier,
  huc8_mncwc_tier,
  ...props
}) => {
  if (!ranked) {
    return null
  }

  const hasStateTiers = networkType === 'dams' && state_ncwc_tier !== -1
  const hasHUC8Tiers = huc8_ncwc_tier !== -1

  if (!(hasStateTiers || hasHUC8Tiers)) {
    return null
  }

  const barrierTypeLabel = barrierTypeLabels[barrierType]

  if (invasive) {
    return (
      <Section title="Connectivity ranks" {...props}>
        <Text style={{ color: '#7f8a93' }}>
          This {barrierTypeLabel} was excluded from prioritization because it
          provides an ecological benefit by restricting the movement of invasive
          aquatic species.
        </Text>
      </Section>
    )
  }

  return (
    <Section
      title="Connectivity ranks"
      {...props}
      wrap={false}
      marginBottom={6}
    >
      <Text
        style={{
          color: '#7f8a93',
          fontSize: 10,
          lineHeight: 1.1,
          textAlign: 'center',
        }}
      >
        connectivity tiers range from 20 (lowest) to 1 (highest)
      </Text>

      {hasStateTiers ? (
        <View style={{ marginTop: 24 }}>
          <Flex style={{ alignItems: 'end', lineHeight: 1.2 }}>
            <View style={{ flex: '1 1 120pt' }}>
              <Text>
                <Italic>
                  Compared to other {barrierTypeLabel} in {STATES[state]}:
                </Italic>
              </Text>
            </View>
            <View style={{ flex: '0 0 120pt' }}>
              <Text style={{ textAlign: 'center' }}>
                <Bold>full network</Bold>
              </Text>
            </View>
            <View style={{ flex: '0 0 120pt' }}>
              <Text style={{ textAlign: 'center' }}>
                <Bold>perennial reaches</Bold>
              </Text>
            </View>
            <View style={{ flex: '0 0 120pt' }}>
              <Text style={{ textAlign: 'center' }}>
                <Bold>mainstem network</Bold>
              </Text>
            </View>
          </Flex>

          <Flex
            style={{
              borderTop: '1px solid #dee1e3',
              marginTop: 6,
              paddingTop: 6,
            }}
          >
            <View style={{ flex: '1 1 120pt' }}>
              <Text>Network connectivity tier</Text>
            </View>
            <View style={{ flex: '0 0 120pt' }}>
              <Text style={{ textAlign: 'center' }}>{state_nc_tier}</Text>
            </View>
            <View style={{ flex: '0 0 120pt' }}>
              <Text style={{ textAlign: 'center' }}>{state_pnc_tier}</Text>
            </View>
            <View style={{ flex: '0 0 120pt' }}>
              <Text style={{ textAlign: 'center' }}>{state_mnc_tier}</Text>
            </View>
          </Flex>

          <Flex
            style={{
              borderTop: '1px solid #dee1e3',
              marginTop: 6,
              paddingTop: 6,
            }}
          >
            <View style={{ flex: '1 1 120pt' }}>
              <Text>Watershed condition tier</Text>
            </View>
            <View style={{ flex: '0 0 120pt' }}>
              <Text style={{ textAlign: 'center' }}>{state_wc_tier}</Text>
            </View>
            <View style={{ flex: '0 0 120pt' }}>
              <Text style={{ textAlign: 'center' }}>{state_pwc_tier}</Text>
            </View>
            <View style={{ flex: '0 0 120pt' }}>
              <Text style={{ textAlign: 'center' }}>{state_mwc_tier}</Text>
            </View>
          </Flex>

          <Flex
            style={{
              borderTop: '1px solid #dee1e3',
              marginTop: 6,
              paddingTop: 6,
            }}
          >
            <View style={{ flex: '1 1 120pt' }}>
              <Text>Combined network connectivity &amp;</Text>
              <Text>watershed condition tier</Text>
            </View>
            <View style={{ flex: '0 0 120pt' }}>
              <Text style={{ textAlign: 'center' }}>{state_ncwc_tier}</Text>
            </View>
            <View style={{ flex: '0 0 120pt' }}>
              <Text style={{ textAlign: 'center' }}>{state_pncwc_tier}</Text>
            </View>
            <View style={{ flex: '0 0 120pt' }}>
              <Text style={{ textAlign: 'center' }}>{state_mncwc_tier}</Text>
            </View>
          </Flex>
        </View>
      ) : null}

      {hasHUC8Tiers ? (
        <View style={{ marginTop: hasStateTiers ? 48 : 24 }}>
          <Flex style={{ alignItems: 'end', lineHeight: 1 }}>
            <View style={{ flex: '1 1 120pt' }}>
              <Text>
                <Italic>
                  Compared to other {barrierTypeLabel} in this subbasin:
                </Italic>
              </Text>
            </View>
            <View style={{ flex: '0 0 120pt', textAlign: 'center' }}>
              <Bold>full</Bold>
              <Bold>network</Bold>
            </View>
            <View style={{ flex: '0 0 120pt', textAlign: 'center' }}>
              <Bold>perennial</Bold>
              <Bold>reaches</Bold>
            </View>
            <View style={{ flex: '0 0 120pt', textAlign: 'center' }}>
              <Bold>mainstem</Bold>
              <Bold>network</Bold>
            </View>
          </Flex>

          <Flex
            style={{
              borderTop: '1px solid #dee1e3',
              marginTop: 6,
              paddingTop: 6,
            }}
          >
            <View style={{ flex: '1 1 120pt' }}>
              <Text>Network connectivity tier</Text>
            </View>
            <View style={{ flex: '0 0 120pt' }}>
              <Text style={{ textAlign: 'center' }}>{huc8_nc_tier}</Text>
            </View>
            <View style={{ flex: '0 0 120pt' }}>
              <Text style={{ textAlign: 'center' }}>{huc8_pnc_tier}</Text>
            </View>
            <View style={{ flex: '0 0 120pt' }}>
              <Text style={{ textAlign: 'center' }}>{huc8_mnc_tier}</Text>
            </View>
          </Flex>

          <Flex
            style={{
              borderTop: '1px solid #dee1e3',
              marginTop: 6,
              paddingTop: 6,
            }}
          >
            <View style={{ flex: '1 1 120pt' }}>
              <Text>Watershed condition tier</Text>
            </View>
            <View style={{ flex: '0 0 120pt' }}>
              <Text style={{ textAlign: 'center' }}>{huc8_wc_tier}</Text>
            </View>
            <View style={{ flex: '0 0 120pt' }}>
              <Text style={{ textAlign: 'center' }}>{huc8_pwc_tier}</Text>
            </View>
            <View style={{ flex: '0 0 120pt' }}>
              <Text style={{ textAlign: 'center' }}>{huc8_mwc_tier}</Text>
            </View>
          </Flex>

          <Flex
            style={{
              borderTop: '1px solid #dee1e3',
              marginTop: 6,
              paddingTop: 6,
            }}
          >
            <View style={{ flex: '1 1 120pt' }}>
              <Text>Combined network connectivity &amp;</Text>
              <Text>watershed condition tier</Text>
            </View>
            <View style={{ flex: '0 0 120pt' }}>
              <Text style={{ textAlign: 'center' }}>{huc8_ncwc_tier}</Text>
            </View>
            <View style={{ flex: '0 0 120pt' }}>
              <Text style={{ textAlign: 'center' }}>{huc8_pncwc_tier}</Text>
            </View>
            <View style={{ flex: '0 0 120pt' }}>
              <Text style={{ textAlign: 'center' }}>{huc8_mncwc_tier}</Text>
            </View>
          </Flex>
        </View>
      ) : null}

      <Text style={{ color: '#7f8a93', marginTop: 28, fontSize: 10 }}>
        Note: network connectivity is based on the total perennial length in a
        given network. Watershed condition is based on the percent of the total
        length of stream reaches in the network that are not altered (canals /
        ditches), the number of unique stream size classes, and the percent of
        natural landcover in the floodplains. Perennial network connectivity is
        based on the total perennial (non-intermittent or ephemeral) length in a
        given network. Perennial watershed condition is based on the percent of
        the total length of perennial stream reaches that are not altered
        (canals / ditches), the number of unique stream size classes in
        perennial reaches, and the percent of natural landcover in the
        floodplains for the full network. Mainstem network connectivity is based
        on the total mainstem network length in a given network. Mainstem
        watershed condition is based on the percent of the total length of
        stream reaches in the mainstem network that are not altered (canals /
        ditches), the number of unique stream size classes in the mainstem
        network, and the percent of natural landcover in the floodplains for the
        full network.
      </Text>
    </Section>
  )
}
Scores.propTypes = {
  barrierType: PropTypes.string.isRequired,
  networkType: PropTypes.string.isRequired,
  state: PropTypes.string.isRequired,
  ranked: PropTypes.bool,
  invasive: PropTypes.bool,
  state_nc_tier: PropTypes.number,
  state_wc_tier: PropTypes.number,
  state_ncwc_tier: PropTypes.number,
  state_pnc_tier: PropTypes.number,
  state_pwc_tier: PropTypes.number,
  state_pncwc_tier: PropTypes.number,
  state_mnc_tier: PropTypes.number,
  state_mwc_tier: PropTypes.number,
  state_mncwc_tier: PropTypes.number,
  huc8_nc_tier: PropTypes.number,
  huc8_wc_tier: PropTypes.number,
  huc8_ncwc_tier: PropTypes.number,
  huc8_pnc_tier: PropTypes.number,
  huc8_pwc_tier: PropTypes.number,
  huc8_pncwc_tier: PropTypes.number,
  huc8_mnc_tier: PropTypes.number,
  huc8_mwc_tier: PropTypes.number,
  huc8_mncwc_tier: PropTypes.number,
}

Scores.defaultProps = {
  ranked: false,
  invasive: false,
  state_nc_tier: null,
  state_wc_tier: null,
  state_ncwc_tier: null,
  state_pnc_tier: null,
  state_pwc_tier: null,
  state_pncwc_tier: null,
  state_mnc_tier: null,
  state_mwc_tier: null,
  state_mncwc_tier: null,
  huc8_nc_tier: null,
  huc8_wc_tier: null,
  huc8_ncwc_tier: null,
  huc8_pnc_tier: null,
  huc8_pwc_tier: null,
  huc8_pncwc_tier: null,
  huc8_mnc_tier: null,
  huc8_mwc_tier: null,
  huc8_mncwc_tier: null,
}

export default Scores
