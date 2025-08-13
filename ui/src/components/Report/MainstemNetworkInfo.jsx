import React from 'react'
import PropTypes from 'prop-types'
import { Text, View } from '@react-pdf/renderer'

import {
  MainstemNetworkPropTypeStub,
  MainstemNetworkDefaultProps,
  LinearDownstreamNetworkPropTypeStub,
  LinearDownstreamNetworkDefaultProps,
} from 'components/BarrierDetails/proptypes'
import { EPA_CAUSE_CODES } from 'config'
import { formatNumber, formatPercent } from 'util/format'

import { Bold, Flex, Link, Section } from './elements'

const columnCSS = {
  marginLeft: 14,
  paddingLeft: 14,
  borderLeft: '1px solid #cfd3d6',
}

const MainstemNetworkInfo = ({
  barrierType,
  networkType,
  totalmainstemupstreammiles,
  perennialmainstemupstreammiles,
  alteredmainstemupstreammiles,
  unalteredmainstemupstreammiles,
  mainstemsizeclasses,
  freemainstemdownstreammiles,
  freeperennialmainstemdownstreammiles,
  freealteredmainstemdownstreammiles,
  freeunalteredmainstemdownstreammiles,
  mainstemupstreamimpairment,
  mainstemdownstreamimpairment,
  removed,
  flowstoocean,
  flowstogreatlakes,
  totaldownstreamdams,
  totaldownstreamsmallbarriers,
  totaldownstreamwaterfalls,
  style,
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

  const mainstemGainMiles = Math.min(
    totalmainstemupstreammiles,
    freemainstemdownstreammiles
  )
  const mainstemGainMilesSide =
    alwaysUseUpstream || mainstemGainMiles === totalmainstemupstreammiles
      ? 'upstream'
      : 'downstream'

  const perennialMainstemGainMiles = Math.min(
    perennialmainstemupstreammiles,
    freeperennialmainstemdownstreammiles
  )
  const perennialMainstemGainMilesSide =
    alwaysUseUpstream ||
    perennialMainstemGainMiles === perennialmainstemupstreammiles
      ? 'upstream'
      : 'downstream'

  const intermittentmainstemupstreammiles =
    totalmainstemupstreammiles - perennialmainstemupstreammiles
  const freeintermittentmainstemdownstreammiles =
    freemainstemdownstreammiles - freeperennialmainstemdownstreammiles

  const percentUnaltered = totalmainstemupstreammiles
    ? (100 * unalteredmainstemupstreammiles) / totalmainstemupstreammiles
    : 0

  const colWidth = totalmainstemupstreammiles > 0 ? 1 / 4 : 1 / 3

  return (
    <Section
      title="Mainstem network information"
      style={style}
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
        Upstream mainstem networks include the stream reaches upstream that are
        the same stream order as the one associated with this barrier (excludes
        smaller tributaries) with at least 1 square mile of drainage area.
        Downstream mainstem networks are based on the linear flow direction
        through the same stream order to the next barrier downstream, a change
        in stream order, or the downstream-most point on the network.
      </Text>

      <Flex>
        <View
          style={{
            flex: `1 1 ${colWidth}%`,
          }}
        >
          <Text>
            <Bold>{formatNumber(mainstemGainMiles, 2, true)} total miles</Bold>{' '}
            {removed ? 'were' : 'could be'} reconnected by removing this{' '}
            {barrierTypeLabel} including{' '}
            <Bold>
              {formatNumber(perennialMainstemGainMiles, 2, true)} miles
            </Bold>{' '}
            of perennial reaches.
          </Text>
        </View>

        {totalmainstemupstreammiles > 0 ? (
          <View
            style={{
              flex: `1 1 ${colWidth}%`,
              ...columnCSS,
            }}
          >
            <Text>
              <Bold>
                {formatPercent(percentUnaltered, 0)}% of the upstream mainstem
                network
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
              {mainstemsizeclasses} mainstem river size{' '}
              {mainstemsizeclasses === 1 ? 'class' : 'classes'}
            </Bold>{' '}
            {removed ? 'were' : 'could be'} gained by removing this{' '}
            {barrierTypeLabel}.
          </Text>
        </View>
      </Flex>

      <View style={{ marginTop: 36 }}>
        <Flex>
          <View style={{ flex: '1 1 auto' }} />
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
              {mainstemGainMilesSide === 'upstream' ? (
                <Bold>{formatNumber(totalmainstemupstreammiles, 2, true)}</Bold>
              ) : (
                <>{formatNumber(totalmainstemupstreammiles, 2, true)}</>
              )}
            </Text>
          </View>
          <View style={{ flex: '0 0 140pt' }}>
            <Text>
              {mainstemGainMilesSide === 'downstream' ? (
                <>
                  <Bold>
                    {formatNumber(freemainstemdownstreammiles, 2, true)}
                  </Bold>
                </>
              ) : (
                <>{formatNumber(freemainstemdownstreammiles, 2, true)}</>
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
              {perennialMainstemGainMilesSide === 'upstream' ? (
                <>
                  <Bold>
                    {formatNumber(perennialmainstemupstreammiles, 2, true)}
                  </Bold>
                </>
              ) : (
                <>{formatNumber(perennialmainstemupstreammiles, 2, true)}</>
              )}
            </Text>
          </View>
          <View style={{ flex: '0 0 140pt' }}>
            <Text>
              {perennialMainstemGainMilesSide === 'downstream' ? (
                <Bold>
                  {formatNumber(freeperennialmainstemdownstreammiles, 2, true)}
                </Bold>
              ) : (
                <>
                  {formatNumber(freeperennialmainstemdownstreammiles, 2, true)}
                </>
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
            <Text>
              {formatNumber(intermittentmainstemupstreammiles, 2, true)}
            </Text>
          </View>
          <View style={{ flex: '0 0 140pt' }}>
            <Text>
              {formatNumber(freeintermittentmainstemdownstreammiles, 2, true)}
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
            <Text>{formatNumber(alteredmainstemupstreammiles, 2, true)}</Text>
          </View>
          <View style={{ flex: '0 0 140pt' }}>
            <Text>
              {formatNumber(freealteredmainstemdownstreammiles, 2, true)}
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
            <Text>Unaltered miles</Text>
          </View>
          <View style={{ flex: '0 0 140pt' }}>
            <Text>{formatNumber(unalteredmainstemupstreammiles, 2, true)}</Text>
          </View>
          <View style={{ flex: '0 0 140pt' }}>
            <Text>
              {formatNumber(freeunalteredmainstemdownstreammiles, 2, true)}
            </Text>
          </View>
        </Flex>

        {mainstemupstreamimpairment || mainstemdownstreamimpairment ? (
          <Flex
            style={{
              borderTop: '1px solid #dee1e3',
              marginTop: 6,
              paddingTop: 6,
            }}
          >
            <View style={{ flex: '1 1 auto' }}>
              <Text>Water quality impairments</Text>
              <Text>present:</Text>
            </View>
            <View style={{ flex: '0 0 140pt', fontSize: 10 }}>
              {mainstemupstreamimpairment
                ? mainstemupstreamimpairment
                    .split(',')
                    .map((code) => (
                      <Text key={code}>{EPA_CAUSE_CODES[code]}</Text>
                    ))
                : null}
            </View>
            <View style={{ flex: '0 0 140pt', fontSize: 10 }}>
              {mainstemdownstreamimpairment
                ? mainstemdownstreamimpairment
                    .split(',')
                    .map((code) => (
                      <Text key={code}>{EPA_CAUSE_CODES[code]}</Text>
                    ))
                : null}
            </View>
          </Flex>
        ) : null}

        {alwaysUseUpstream ? (
          <Text style={{ color: '#7f8a93', marginTop: 28, fontSize: 10 }}>
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
          .
          {mainstemupstreamimpairment || mainstemdownstreamimpairment ? (
            <>
              <br />
              <br />
              Water quality impairments based on based on{' '}
              <Link href="https://www.epa.gov/waterdata/attains">
                EPA ATTAINS
              </Link>{' '}
              water quality data within the mainstem network.
            </>
          ) : null}
        </Text>
      </View>
    </Section>
  )
}

MainstemNetworkInfo.propTypes = {
  ...MainstemNetworkPropTypeStub,
  ...LinearDownstreamNetworkPropTypeStub,
  barrierType: PropTypes.string.isRequired,
  networkType: PropTypes.string.isRequired,
  removed: PropTypes.bool,
  style: PropTypes.object,
}

MainstemNetworkInfo.defaultProps = {
  ...MainstemNetworkDefaultProps,
  ...LinearDownstreamNetworkDefaultProps,
  removed: false,
  style: null,
}

export default MainstemNetworkInfo
