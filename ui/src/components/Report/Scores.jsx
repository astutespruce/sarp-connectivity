/* eslint-disable camelcase */
import React from 'react'
import PropTypes from 'prop-types'
import { Text, View } from '@react-pdf/renderer'

import { Bold, Flex, Italic, Section } from './elements'
import { barrierTypeLabels } from '../../../config/constants'

const Scores = ({
  barrierType,
  state,
  hasnetwork,
  ranked,
  state_nc_tier,
  state_wc_tier,
  state_ncwc_tier,
  state_pnc_tier,
  state_pwc_tier,
  state_pncwc_tier,
  se_nc_tier,
  se_wc_tier,
  se_ncwc_tier,
  se_pnc_tier,
  se_pwc_tier,
  se_pncwc_tier,
  ...props
}) => {
  if (!hasnetwork) {
    return null
  }

  if (!ranked) {
    return (
      <Section title="Connectivity ranks" {...props}>
        <Text style={{ color: '#7f8a93' }}>
          This {typeLabel} was excluded from prioritization because it provides
          an ecological benefit by restricting the movement of invasive aquatic
          species.
        </Text>
      </Section>
    )
  }

  const hasSoutheast =
    se_nc_tier !== null && se_nc_tier !== undefined && se_nc_tier !== -1

  const barrierTypeLabel = barrierTypeLabels[barrierType]

  const typeLabel = barrierType === 'dams' ? 'dam' : 'road-related barrier'
  return (
    <Section title="Connectivity ranks" {...props}>
      <Text style={{ color: '#7f8a93', fontSize: 10 }}>
        connectivity tiers range from 20 (lowest) to 1 (highest)
      </Text>

      <View style={{ marginTop: 24 }}>
        <Flex>
          <View style={{ flex: '1 1 160pt' }}>
            <Text>
              <Italic>
                Compared to other {barrierTypeLabel} in {state}:
              </Italic>
            </Text>
          </View>
          <View style={{ flex: '1 1 auto' }}>
            <Text>
              <Bold>full network</Bold>
            </Text>
          </View>
          <View style={{ flex: '1 1 60pt' }}>
            <Text>
              <Bold>perennial segments only</Bold>
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
          <View style={{ flex: '1 1 160pt' }}>
            <Text>Network connectivity tier</Text>
          </View>
          <View style={{ flex: '1 1 auto' }}>
            <Text>{state_nc_tier}</Text>
          </View>
          <View style={{ flex: '1 1 60pt' }}>
            <Text>{state_pnc_tier}</Text>
          </View>
        </Flex>

        <Flex
          style={{
            borderTop: '1px solid #dee1e3',
            marginTop: 6,
            paddingTop: 6,
          }}
        >
          <View style={{ flex: '1 1 160pt' }}>
            <Text>Watershed condition tier</Text>
          </View>
          <View style={{ flex: '1 1 auto' }}>
            <Text>{state_wc_tier}</Text>
          </View>
          <View style={{ flex: '1 1 60pt' }}>
            <Text>{state_pwc_tier}</Text>
          </View>
        </Flex>

        <Flex
          style={{
            borderTop: '1px solid #dee1e3',
            marginTop: 6,
            paddingTop: 6,
          }}
        >
          <View style={{ flex: '1 1 160pt' }}>
            <Text>Combined network connectivity &amp;</Text>
            <Text>watershed condition tier</Text>
          </View>
          <View style={{ flex: '1 1 auto' }}>
            <Text>{state_ncwc_tier}</Text>
          </View>
          <View style={{ flex: '1 1 60pt' }}>
            <Text>{state_pncwc_tier}</Text>
          </View>
        </Flex>

        {hasSoutheast ? (
          <View style={{ marginTop: 24 }}>
            <Flex>
              <View style={{ flex: '1 1 160pt' }}>
                <Text>
                  <Italic>
                    Compared to other {barrierTypeLabel} in the Southeast:
                  </Italic>
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
              <View style={{ flex: '1 1 160pt' }}>
                <Text>Network connectivity tier</Text>
              </View>
              <View style={{ flex: '1 1 auto' }}>
                <Text>{se_nc_tier}</Text>
              </View>
              <View style={{ flex: '1 1 60pt' }}>
                <Text>{se_pnc_tier}</Text>
              </View>
            </Flex>

            <Flex
              style={{
                borderTop: '1px solid #dee1e3',
                marginTop: 6,
                paddingTop: 6,
              }}
            >
              <View style={{ flex: '1 1 160pt' }}>
                <Text>Watershed condition tier</Text>
              </View>
              <View style={{ flex: '1 1 auto' }}>
                <Text>{se_wc_tier}</Text>
              </View>
              <View style={{ flex: '1 1 60pt' }}>
                <Text>{se_pwc_tier}</Text>
              </View>
            </Flex>

            <Flex
              style={{
                borderTop: '1px solid #dee1e3',
                marginTop: 6,
                paddingTop: 6,
              }}
            >
              <View style={{ flex: '1 1 160pt' }}>
                <Text>Combined network connectivity &amp;</Text>
                <Text>watershed condition tier</Text>
              </View>
              <View style={{ flex: '1 1 auto' }}>
                <Text>{se_ncwc_tier}</Text>
              </View>
              <View style={{ flex: '1 1 60pt' }}>
                <Text>{se_pncwc_tier}</Text>
              </View>
            </Flex>
          </View>
        ) : null}

        <Text style={{ color: '#7f8a93', marginTop: 28, fontSize: 10 }}>
          Note: perennial network connectivity is based on the total perennial
          (non-intermittent or ephemeral) length in a given network. Perennial
          watershed condition is based partly upon the percent of the perennial
          stream reaches that are not altered (canals / ditches)
        </Text>
      </View>
    </Section>
  )
}
Scores.propTypes = {
  barrierType: PropTypes.string.isRequired,
  state: PropTypes.string.isRequired,
  hasnetwork: PropTypes.bool,
  ranked: PropTypes.bool,
  state_nc_tier: PropTypes.number,
  state_wc_tier: PropTypes.number,
  state_ncwc_tier: PropTypes.number,
  state_pnc_tier: PropTypes.number,
  state_pwc_tier: PropTypes.number,
  state_pncwc_tier: PropTypes.number,
  se_nc_tier: PropTypes.number,
  se_wc_tier: PropTypes.number,
  se_ncwc_tier: PropTypes.number,
  se_pnc_tier: PropTypes.number,
  se_pwc_tier: PropTypes.number,
  se_pncwc_tier: PropTypes.number,
}

Scores.defaultProps = {
  hasnetwork: false,
  ranked: false,
  state_nc_tier: null,
  state_wc_tier: null,
  state_ncwc_tier: null,
  state_pnc_tier: null,
  state_pwc_tier: null,
  state_pncwc_tier: null,
  se_nc_tier: null,
  se_wc_tier: null,
  se_ncwc_tier: null,
  se_pnc_tier: null,
  se_pwc_tier: null,
  se_pncwc_tier: null,
}

export default Scores
