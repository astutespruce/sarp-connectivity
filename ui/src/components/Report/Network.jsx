import React from 'react'
import PropTypes from 'prop-types'
import { Text, View } from '@react-pdf/renderer'

import { formatNumber, formatPercent } from 'util/format'

import { Bold, Flex, Italic, Link, Section } from './elements'
import { siteMetadata } from '../../../gatsby-config'

const { version: dataVersion } = siteMetadata

const columnCSS = {
  marginLeft: 14,
  paddingLeft: 14,
  borderLeft: '1px solid #cfd3d6',
}

const Network = ({
  sarpid,
  barrierType,
  totalupstreammiles,
  perennialupstreammiles,
  alteredupstreammiles,
  unalteredupstreammiles,
  freedownstreammiles,
  freeperennialdownstreammiles,
  freealtereddownstreammiles,
  freeunaltereddownstreammiles,
  sizeclasses,
  landcover,
  excluded,
  hasnetwork,
  ...props
}) => {
  const barrierTypeLabel =
    barrierType === 'dams' ? 'dam' : 'road-related barrier'
  const gainmiles = Math.min(totalupstreammiles, freedownstreammiles)
  const gainMilesSide =
    gainmiles === totalupstreammiles ? 'upstream' : 'downstream'

  const perennialGainMiles = Math.min(
    perennialupstreammiles,
    freeperennialdownstreammiles
  )
  const perennialGainMilesSide =
    perennialGainMiles === perennialupstreammiles ? 'upstream' : 'downstream'

  const intermittentupstreammiles = totalupstreammiles - perennialupstreammiles
  const freeintermittentdownstreammiles =
    freedownstreammiles - freeperennialdownstreammiles

  const percentAltered = totalupstreammiles
    ? (100 * alteredupstreammiles) / totalupstreammiles
    : 0

  const colWidth = totalupstreammiles > 0 ? 1 / 4 : 1 / 3

  if (excluded) {
    return (
      <Section title="Functional network information" {...props}>
        <Text>
          This {barrierTypeLabel} was excluded from the connectivity analysis
          based on field reconnaissance or manual review of aerial imagery.
        </Text>
      </Section>
    )
  }

  if (!hasnetwork) {
    return (
      <Section title="Functional network information" {...props}>
        <Text>
          This {barrierTypeLabel} is off-network and has no functional network
          information.
          {'\n\n'}
        </Text>
        <Text style={{ color: '#7f8a93' }}>
          Not all {barrierType} could be correctly snapped to the aquatic
          network for analysis. Please{' '}
          <Link
            href={`mailto:Kat@southeastaquatics.net?subject=Problem with SARP Inventory for ${
              barrierType === 'dams' ? 'dam' : 'road-related barrier'
            }: ${sarpid} (data version: ${dataVersion})&body=I found the following problem with the SARP Inventory for this barrier:`}
          >
            contact us
          </Link>{' '}
          to report an error or for assistance interpreting these results.
        </Text>
      </Section>
    )
  }

  return (
    <Section title="Functional network information" {...props}>
      <Flex>
        <View
          style={{
            flex: `1 1 ${colWidth}%`,
          }}
        >
          <Text>
            <Bold>{formatNumber(gainmiles, 2, true)} total miles</Bold> could be
            reconnected by removing this {barrierTypeLabel}, including{' '}
            <Bold>{formatNumber(perennialGainMiles, 2, true)} miles</Bold> of
            perennial reaches.
          </Text>
        </View>

        {totalupstreammiles > 0 ? (
          <View
            style={{
              flex: `1 1 ${colWidth}%`,
              ...columnCSS,
            }}
          >
            <Text>
              <Bold>
                {formatPercent(percentAltered, 0)}% of the upstream network
              </Bold>{' '}
              is in altered stream channels (coded as canals / ditches).
            </Text>
          </View>
        ) : null}

        <View
          style={{
            flex: `1 1 ${colWidth}%`,
            ...columnCSS,
          }}
        >
          <Text>
            <Bold>
              {sizeclasses} river size {sizeclasses === 1 ? 'class' : 'classes'}
            </Bold>{' '}
            could be gained by removing this barrier.
          </Text>
        </View>

        <View
          style={{
            flex: `1 1 ${colWidth}%`,
            ...columnCSS,
          }}
        >
          <Text>
            <Bold>
              {formatNumber(landcover, 0)}% of the upstream floodplain
            </Bold>{' '}
            is composed of natural landcover.
          </Text>
        </View>
      </Flex>

      <View style={{ marginTop: 36 }}>
        <Flex>
          <View style={{ flex: '1 1 160pt' }}>
            <Text>
              <Italic>Network statistics:</Italic>
            </Text>
          </View>
          <View style={{ flex: '1 1 auto' }}>
            <Text>
              <Bold>upstream network</Bold>
            </Text>
          </View>
          <View style={{ flex: '1 1 auto' }}>
            <Text>
              <Bold>downstream network</Bold>
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
            <Text>Total miles</Text>
          </View>
          <View style={{ flex: '1 1 auto' }}>
            <Text>
              {gainMilesSide === 'upstream' ? (
                <Bold>{formatNumber(totalupstreammiles, 2, true)}</Bold>
              ) : (
                <>{formatNumber(totalupstreammiles, 2, true)}</>
              )}
            </Text>
          </View>
          <View style={{ flex: '1 1 auto' }}>
            <Text>
              {gainMilesSide === 'downstream' ? (
                <Bold>{formatNumber(freedownstreammiles, 2, true)}</Bold>
              ) : (
                <>{formatNumber(freedownstreammiles, 2, true)}</>
              )}
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
            <Text>Perennial miles</Text>
          </View>
          <View style={{ flex: '1 1 auto' }}>
            <Text>
              {perennialGainMilesSide === 'upstream' ? (
                <Bold>{formatNumber(perennialupstreammiles, 2, true)}</Bold>
              ) : (
                <>{formatNumber(perennialupstreammiles, 2, true)}</>
              )}
            </Text>
          </View>
          <View style={{ flex: '1 1 auto' }}>
            <Text>
              {perennialGainMilesSide === 'downstream' ? (
                <Bold>
                  {formatNumber(freeperennialdownstreammiles, 2, true)}
                </Bold>
              ) : (
                <>{formatNumber(freeperennialdownstreammiles, 2, true)}</>
              )}
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
            <Text>Ephemeral / intermittent miles</Text>
          </View>
          <View style={{ flex: '1 1 auto' }}>
            <Text>{formatNumber(intermittentupstreammiles, 2, true)}</Text>
          </View>
          <View style={{ flex: '1 1 auto' }}>
            <Text>
              {formatNumber(freeintermittentdownstreammiles, 2, true)}
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
            <Text>Altered miles</Text>
          </View>
          <View style={{ flex: '1 1 auto' }}>
            <Text>{formatNumber(alteredupstreammiles, 2, true)}</Text>
          </View>
          <View style={{ flex: '1 1 auto' }}>
            <Text>{formatNumber(freealtereddownstreammiles, 2, true)}</Text>
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
            <Text>Unaltered miles</Text>
          </View>
          <View style={{ flex: '1 1 auto' }}>
            <Text>{formatNumber(unalteredupstreammiles, 2, true)}</Text>
          </View>
          <View style={{ flex: '1 1 auto' }}>
            <Text>{formatNumber(freeunaltereddownstreammiles, 2, true)}</Text>
          </View>
        </Flex>

        <Text style={{ color: '#7f8a93', marginTop: 28, fontSize: 10 }}>
          Note: downstream lengths are limited to free-flowing reaches only;
          these exclude lengths within waterbodies in the downstream network.
          Perennial miles are the sum of lengths of all reaches not specifically
          coded as ephemeral or intermittent within the functional network.
          Perennial reaches are not necessarily contiguous. Altered miles are
          those that are specifically coded as canals or ditches, and do not
          necessarily include all forms of alteration of the stream channel.
        </Text>
      </View>
    </Section>
  )
}

Network.propTypes = {
  sarpid: PropTypes.string.isRequired,
  barrierType: PropTypes.string.isRequired,
  hasnetwork: PropTypes.bool.isRequired,
  excluded: PropTypes.bool,
  totalupstreammiles: PropTypes.number,
  perennialupstreammiles: PropTypes.number,
  alteredupstreammiles: PropTypes.number,
  unalteredupstreammiles: PropTypes.number,
  freedownstreammiles: PropTypes.number,
  freeperennialdownstreammiles: PropTypes.number,
  freealtereddownstreammiles: PropTypes.number,
  freeunaltereddownstreammiles: PropTypes.number,
  landcover: PropTypes.number,
  sizeclasses: PropTypes.number,
}

Network.defaultProps = {
  excluded: false,
  totalupstreammiles: 0,
  perennialupstreammiles: 0,
  alteredupstreammiles: 0,
  unalteredupstreammiles: 0,
  freedownstreammiles: 0,
  freeperennialdownstreammiles: 0,
  freealtereddownstreammiles: 0,
  freeunaltereddownstreammiles: 0,
  landcover: 0,
  sizeclasses: 0,
}

export default Network
