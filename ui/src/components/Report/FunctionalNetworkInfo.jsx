import React from 'react'
import PropTypes from 'prop-types'
import { Text, View } from '@react-pdf/renderer'

import { siteMetadata } from 'config'
import {
  FunctionalNetworkPropTypeStub,
  FunctionalNetworkDefaultProps,
  LinearDownstreamNetworkPropTypeStub,
  LinearDownstreamNetworkDefaultProps,
} from 'components/BarrierDetails/proptypes'
import { formatNumber, formatPercent } from 'util/format'

import { Bold, Flex, Italic, Link, Section } from './elements'

const { version: dataVersion } = siteMetadata

const columnCSS = {
  marginLeft: 14,
  paddingLeft: 14,
  borderLeft: '1px solid #cfd3d6',
}

const FunctionalNetworkInfo = ({
  sarpid,
  barrierType,
  networkType,
  totalupstreammiles,
  perennialupstreammiles,
  alteredupstreammiles,
  unalteredupstreammiles,
  resilientupstreammiles,
  coldupstreammiles,
  freedownstreammiles,
  freeperennialdownstreammiles,
  freealtereddownstreammiles,
  freeunaltereddownstreammiles,
  freeresilientdownstreammiles,
  freecolddownstreammiles,
  sizeclasses,
  landcover,
  excluded,
  onloop,
  diversion,
  hasnetwork,
  in_network_type,
  invasive,
  unranked,
  removed,
  yearremoved,
  flowstoocean,
  flowstogreatlakes,
  totaldownstreamdams,
  totaldownstreamsmallbarriers,
  totaldownstreamwaterfalls,
  unalteredwaterbodyacres,
  unalteredwetlandacres,
  ...props
}) => {
  const barrierTypeLabel =
    barrierType === 'dams' ? 'dam' : 'road-related barrier'

  const totaldownstreambarriers =
    networkType === 'dams'
      ? totaldownstreamdams + totaldownstreamwaterfalls
      : totaldownstreamdams +
        totaldownstreamwaterfalls +
        totaldownstreamsmallbarriers

  const alwaysUseUpstream =
    (flowstoocean === 1 || flowstogreatlakes === 1) &&
    totaldownstreambarriers === 0

  const gainmiles = Math.min(totalupstreammiles, freedownstreammiles)
  const gainMilesSide =
    alwaysUseUpstream || gainmiles === totalupstreammiles
      ? 'upstream'
      : 'downstream'

  const perennialGainMiles = Math.min(
    perennialupstreammiles,
    freeperennialdownstreammiles
  )
  const perennialGainMilesSide =
    alwaysUseUpstream || perennialGainMiles === perennialupstreammiles
      ? 'upstream'
      : 'downstream'

  const intermittentupstreammiles = totalupstreammiles - perennialupstreammiles
  const freeintermittentdownstreammiles =
    freedownstreammiles - freeperennialdownstreammiles

  const percentUnaltered = totalupstreammiles
    ? (100 * unalteredupstreammiles) / totalupstreammiles
    : 0

  const colWidth = totalupstreammiles > 0 ? 1 / 4 : 1 / 3

  if (excluded) {
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
            : null}{' '}
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
      <Text
        style={{
          color: '#7f8a93',
          fontSize: 10,
          lineHeight: 1.2,
          marginBottom: '6pt',
        }}
      >
        Functional networks are the full upstream dendritic network to the
        upstream-most points on the network or upstream barriers. The downstream
        network is the upstream functional network of the next barrier
        immediately downstream or downstream-most point on that network, and
        includes any tributaries up to their upstream-most points or other
        barriers.
      </Text>

      {removed ? (
        <Text style={{ marginBottom: '12pt' }}>
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
            <Bold>{formatNumber(gainmiles, 2, true)} total miles</Bold>{' '}
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
                {formatPercent(percentUnaltered, 0)}% of the upstream network
              </Bold>{' '}
              is in unaltered stream reaches.
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
                <>
                  <Bold>{formatNumber(freedownstreammiles, 2, true)}</Bold>
                </>
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
                <>
                  <Bold>{formatNumber(perennialupstreammiles, 2, true)}</Bold>
                </>
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

        <Flex
          style={{
            borderTop: '1px solid #dee1e3',
            marginTop: 6,
            paddingTop: 6,
          }}
        >
          <View style={{ flex: '1 1 auto' }}>
            <Text>Resilient miles</Text>
          </View>
          <View style={{ flex: '0 0 140pt' }}>
            <Text>{formatNumber(resilientupstreammiles, 2, true)}</Text>
          </View>
          <View style={{ flex: '0 0 140pt' }}>
            <Text>{formatNumber(freeresilientdownstreammiles, 2, true)}</Text>
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
            <Text>Coldwater habitat miles</Text>
          </View>
          <View style={{ flex: '0 0 140pt' }}>
            <Text>{formatNumber(coldupstreammiles, 2, true)}</Text>
          </View>
          <View style={{ flex: '0 0 140pt' }}>
            <Text>{formatNumber(freecolddownstreammiles, 2, true)}</Text>
          </View>
        </Flex>

        <View style={{ marginTop: 28 }}>
          <Text>
            This network intersects{' '}
            <Bold>{formatNumber(unalteredwaterbodyacres)} acres</Bold> of
            unaltered lakes and ponds and{' '}
            <Bold>{formatNumber(unalteredwetlandacres)} acres</Bold> of
            unaltered freshwater wetlands.
          </Text>
        </View>

        {unranked && !invasive ? (
          <Text
            style={{
              color: '#7f8a93',
              marginTop: 28,
              fontSize: 10,
              lineHeight: 1.2,
            }}
          >
            Note: this {barrierTypeLabel} excluded from ranking based on field
            reconnaissance, manual review of aerial imagery, or other
            information about this {barrierTypeLabel}.
          </Text>
        ) : null}

        {alwaysUseUpstream ? (
          <Text
            style={{
              color: '#7f8a93',
              marginTop: 28,
              fontSize: 10,
              lineHeight: 1.2,
            }}
          >
            Note: upstream miles are used because the downstream network flows
            into the {flowstogreatlakes === 1 ? 'Great Lakes' : 'ocean'} and
            there are no barriers downstream.
          </Text>
        ) : null}

        <Text
          style={{
            color: '#7f8a93',
            marginTop: alwaysUseUpstream ? 14 : 28,
            fontSize: 10,
            lineHeight: 1.2,
          }}
        >
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
          Resilient miles are the total length of stream reaches that are within
          watersheds with above average or greater freshwater resilience within{' '}
          <Link href="https://www.maps.tnc.org/resilientrivers/#/explore">
            The Nature Conservancy&apos;s Freshwater Resilience
          </Link>{' '}
          dataset (v0.44). Coldwater habitat miles are the total length of
          stream reaches that are within watersheds with slighly above average
          or greater cold temperature scores (TNC, March 2024).
        </Text>
        <Text
          style={{
            marginTop: 14,
            color: '#7f8a93',
            fontSize: 10,
            lineHeight: 1.2,
          }}
        >
          Unaltered lakes and ponds include any that intersect a stream reach in
          the upstream functional network, and exclude any specifically marked
          by their data provider as altered as well as any that are associated
          with dams in this inventory. Unaltered freshwater wetlands are derived
          from the National Wetlands Inventory (freshwater scrub-shrub,
          freshwater forested, freshwater emergent) and NHD (swamp/marsh) and
          exclude any specifically marked by their data provider as altered.
        </Text>
      </View>
    </Section>
  )
}

FunctionalNetworkInfo.propTypes = {
  ...FunctionalNetworkPropTypeStub,
  ...LinearDownstreamNetworkPropTypeStub,
  sarpid: PropTypes.string.isRequired,
  barrierType: PropTypes.string.isRequired,
  networkType: PropTypes.string.isRequired,
  hasnetwork: PropTypes.bool.isRequired,
  in_network_type: PropTypes.bool.isRequired,
  excluded: PropTypes.bool,
  onloop: PropTypes.bool,
  diversion: PropTypes.number,
  invasive: PropTypes.bool,
  unranked: PropTypes.bool,
  removed: PropTypes.bool,
  yearremoved: PropTypes.number,
}

FunctionalNetworkInfo.defaultProps = {
  ...FunctionalNetworkDefaultProps,
  ...LinearDownstreamNetworkDefaultProps,
  excluded: false,
  onloop: false,
  diversion: 0,
  invasive: false,
  unranked: false,
  removed: false,
  yearremoved: 0,
}

export default FunctionalNetworkInfo
