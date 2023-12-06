import React from 'react'
import PropTypes from 'prop-types'
import { Text, View } from '@react-pdf/renderer'

import { siteMetadata } from 'config'
import { formatNumber, formatPercent } from 'util/format'

import { Bold, Flex, Italic, Link, Section } from './elements'

const { version: dataVersion } = siteMetadata

const columnCSS = {
  marginLeft: 14,
  paddingLeft: 14,
  borderLeft: '1px solid #cfd3d6',
}

const Network = ({
  sarpid,
  barrierType,
  networkType,
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
  onloop,
  diversion,
  nostructure,
  hasnetwork,
  in_network_type,
  invasive,
  unranked,
  removed,
  yearremoved,
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
    if (diversion && nostructure) {
      return (
        <Section title="Functional network information" {...props} wrap={false}>
          <Text>
            This water diversion was excluded from the connectivity analysis
            because it does not have an associated in-stream barrier.
          </Text>
        </Section>
      )
    }

    return (
      <Section title="Functional network information" {...props} wrap={false}>
        <Text>
          This {barrierTypeLabel} was excluded from the connectivity analysis
          based on field reconnaissance or manual review of aerial imagery.
        </Text>
      </Section>
    )
  }

  if (onloop) {
    return (
      <Section title="Functional network information" {...props} wrap={false}>
        <Text>
          This {barrierTypeLabel} was excluded from the connectivity analysis
          based on its position within the aquatic network.
          {'\n\n'}
        </Text>

        <Text style={{ color: '#7f8a93' }}>
          This {barrierType === 'dams' ? 'dam' : 'road-related barrier'} was
          snapped to a secondary channel within the aquatic network according to
          the way that primary versus secondary channels are identified within
          the NHD High Resolution Plus dataset. This{' '}
          {barrierType === 'dams' ? 'dam' : 'road-related barrier'} may need to
          be repositioned to occur on the primary channel in order to be
          included within the connectivity analysis. Please{' '}
          <Link
            href={`mailto:Kat@southeastaquatics.net?subject=Problem with SARP Inventory for ${
              barrierType === 'dams' ? 'dam' : 'road-related barrier'
            }: ${sarpid} (data version: ${dataVersion})&body=I found the following problem with the SARP Inventory for this barrier:`}
          >
            contact us
          </Link>{' '}
          to report an error.
        </Text>
      </Section>
    )
  }
  if (!in_network_type) {
    return (
      <Section title="Functional network information" {...props} wrap={false}>
        <Text>
          This {barrierTypeLabel} is not included in this network scenario based
          on its passability
          {networkType === 'largefish_barriers'
            ? ' for large-bodied fish '
            : null}
          {networkType === 'smallfish_barriers'
            ? ' for small-bodied fish '
            : null}
          and has no functional network information.
          {'\n\n'}
        </Text>
      </Section>
    )
  }

  if (!hasnetwork) {
    return (
      <Section title="Functional network information" {...props} wrap={false}>
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
    <Section
      title="Functional network information"
      {...props}
      wrap={false}
      marginBottom={6}
    >
      {removed ? (
        <Text style={{ marginBottom: `12pt` }}>
          {yearremoved !== null && yearremoved > 0
            ? `This barrier was removed or mitigated in ${yearremoved}.`
            : 'This barrier has been removed or mitigated.'}
        </Text>
      ) : null}

      <Flex>
        <View
          style={{
            flex: `1 1 ${colWidth}%`,
          }}
        >
          <Text>
            <Bold>{formatNumber(gainmiles, 2, true)} total miles</Bold>
            {removed ? 'were' : 'could be'} reconnected by removing this{' '}
            {barrierTypeLabel} including{' '}
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
              is in altered stream reaches.
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
            {removed ? 'were' : 'could be'} gained by removing this{' '}
            {barrierTypeLabel}.
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
          <View style={{ flex: '1 1 auto' }}>
            <Text>
              <Italic>Network statistics:</Italic>
            </Text>
          </View>
          <View style={{ flex: '0 0 140pt' }}>
            <Text>
              <Bold>upstream network</Bold>
            </Text>
          </View>
          <View style={{ flex: '0 0 140pt' }}>
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
          <View style={{ flex: '1 1 auto' }}>
            <Text>Total miles</Text>
          </View>
          <View style={{ flex: '0 0 140pt' }}>
            <Text>
              {gainMilesSide === 'upstream' ? (
                <Bold>{formatNumber(totalupstreammiles, 2, true)}</Bold>
              ) : (
                <>{formatNumber(totalupstreammiles, 2, true)}</>
              )}
            </Text>
          </View>
          <View style={{ flex: '0 0 140pt' }}>
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
          <View style={{ flex: '1 1 auto' }}>
            <Text>Perennial miles</Text>
          </View>
          <View style={{ flex: '0 0 140pt' }}>
            <Text>
              {perennialGainMilesSide === 'upstream' ? (
                <Bold>{formatNumber(perennialupstreammiles, 2, true)}</Bold>
              ) : (
                <>{formatNumber(perennialupstreammiles, 2, true)}</>
              )}
            </Text>
          </View>
          <View style={{ flex: '0 0 140pt' }}>
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
          <View style={{ flex: '1 1 auto' }}>
            <Text>Ephemeral / intermittent miles</Text>
          </View>
          <View style={{ flex: '0 0 140pt' }}>
            <Text>{formatNumber(intermittentupstreammiles, 2, true)}</Text>
          </View>
          <View style={{ flex: '0 0 140pt' }}>
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
          <View style={{ flex: '1 1 auto' }}>
            <Text>Altered miles</Text>
          </View>
          <View style={{ flex: '0 0 140pt' }}>
            <Text>{formatNumber(alteredupstreammiles, 2, true)}</Text>
          </View>
          <View style={{ flex: '0 0 140pt' }}>
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
          <View style={{ flex: '1 1 auto' }}>
            <Text>Unaltered miles</Text>
          </View>
          <View style={{ flex: '0 0 140pt' }}>
            <Text>{formatNumber(unalteredupstreammiles, 2, true)}</Text>
          </View>
          <View style={{ flex: '0 0 140pt' }}>
            <Text>{formatNumber(freeunaltereddownstreammiles, 2, true)}</Text>
          </View>
        </Flex>

        {invasive ? (
          <Text style={{ color: '#7f8a93', marginTop: 28, fontSize: 10 }}>
            Note: this {barrierTypeLabel} is identified as a beneficial to
            restricting the movement of invasive species and is not ranked.
          </Text>
        ) : null}

        {unranked && !invasive ? (
          <Text style={{ color: '#7f8a93', marginTop: 28, fontSize: 10 }}>
            Note: this {barrierTypeLabel} excluded from ranking based on field
            reconnaissance, manual review of aerial imagery, or other
            information about this {barrierTypeLabel}.
          </Text>
        ) : null}

        <Text style={{ color: '#7f8a93', marginTop: 28, fontSize: 10 }}>
          Note: statistics are based on aquatic networks cut by{' '}
          {networkType === 'dams'
            ? 'waterfalls and dams'
            : 'waterfalls, dams, and road-related barriers'}
          {networkType === 'largefish_barriers'
            ? ' based on their passability for large-bodied fish'
            : null}
          {networkType === 'smallfish_barriers'
            ? ' based on their passability for small-bodied fish'
            : null}
          {removed
            ? `, including any that were present at the time this ${barrierTypeLabel} was removed, with the exception of those directly upstream that were removed in the same year as this barrier. All barriers removed prior to 2000 or where the year they were removed was unknown were lumped together for this analysis`
            : null}
          . Downstream lengths are limited to free-flowing reaches only; these
          exclude lengths within waterbodies in the downstream network.
          Perennial miles are the sum of lengths of all reaches not specifically
          coded as ephemeral or intermittent within the functional network.
          Perennial reaches are not necessarily contiguous. Altered miles are
          the total length of stream reaches that are specifically identified in
          NHD or the National Wetlands Inventory as altered (canal / ditch,
          within a reservoir, or other channel alteration), and do not
          necessarily include all forms of alteration of the stream channel.
        </Text>
      </View>
    </Section>
  )
}

Network.propTypes = {
  sarpid: PropTypes.string.isRequired,
  barrierType: PropTypes.string.isRequired,
  networkType: PropTypes.string.isRequired,
  hasnetwork: PropTypes.bool.isRequired,
  in_network_type: PropTypes.bool.isRequired,
  excluded: PropTypes.bool,
  onloop: PropTypes.bool,
  diversion: PropTypes.number,
  nostructure: PropTypes.oneOfType([PropTypes.bool, PropTypes.number]),
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
  invasive: PropTypes.bool,
  unranked: PropTypes.bool,
  removed: PropTypes.bool,
  yearremoved: PropTypes.number,
}

Network.defaultProps = {
  excluded: false,
  onloop: false,
  diversion: 0,
  nostructure: false,
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
  invasive: false,
  unranked: false,
  removed: false,
  yearremoved: 0,
}

export default Network
