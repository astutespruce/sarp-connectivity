import React from 'react'
import PropTypes from 'prop-types'
import { Box, Text } from 'theme-ui'

import { barrierTypeLabelSingular } from 'config'
import { Table, Row } from 'components/Table'
import { InfoTooltip } from 'components/Tooltip'
import { Entry, Field } from 'components/Sidebar'
import { formatNumber, formatPercent } from 'util/format'
import {
  MainstemNetworkPropTypeStub,
  MainstemNetworkDefaultProps,
} from './proptypes'

const activeSideCSS = {
  fontWeight: 'bold',
}
const inactiveSideCSS = {
  visibility: 'hidden',
}

const MainstemNetworkInfo = ({
  barrierType,
  networkType,
  totalmainstemupstreammiles,
  perennialmainstemupstreammiles,
  alteredmainstemupstreammiles,
  unalteredmainstemupstreammiles,
  freemainstemdownstreammiles,
  freeperennialmainstemdownstreammiles,
  freealteredmainstemdownstreammiles,
  freeunalteredmainstemdownstreammiles,
  mainstemsizeclasses,
  fontSize,
  headerFontSize,
  removed,
  flowstoocean,
  flowstogreatlakes,
  totaldownstreamdams,
  totaldownstreamsmallbarriers,
  totaldownstreamwaterfalls,
}) => {
  const barrierTypeLabel = barrierTypeLabelSingular[barrierType]

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

  return (
    <Box>
      <Text variant="help" sx={{ fontSize: 0 }}>
        <Text variant="help" sx={{ fontSize: 0, mx: '0.5rem', mb: '1rem' }}>
          Upstream mainstem networks include the stream reaches upstream that
          are the same stream order as the one associated with this barrier
          (excludes smaller tributaries) with at least 1 square mile of drainage
          area. Downstream mainstem networks are based on the linear flow
          direction through the same stream order to the next barrier
          downstream, a change in stream order, or the downstream-most point on
          that network.
        </Text>
      </Text>
      <Entry>
        <Table sx={{ fontSize }} columns="11rem 1fr 1fr">
          <Row sx={{ px: '0.5rem' }}>
            <Box />
            <Box sx={{ fontSize: headerFontSize }}>
              <b>Upstream</b>
            </Box>
            <Box sx={{ fontSize: headerFontSize }}>
              <b>Downstream</b>
              <br />
              <Text sx={{ fontSize: headerFontSize, color: 'grey.7' }}>
                free-flowing miles only
              </Text>
            </Box>
          </Row>

          <Row sx={{ px: '0.5rem' }}>
            <Box>
              <Text sx={{ display: 'inline' }}>Total miles</Text>
              <Box sx={{ display: 'inline-block' }}>
                <InfoTooltip>
                  Total mainstem miles upstream is the sum of all river and
                  stream lengths in contiguous stream reaches of the same stream
                  order order as this
                  {barrierTypeLabel} and with drainage area ≥ 1 square mile.
                  <br />
                  <br />
                  Total mainstem miles downstream is the sum of all river and
                  stream lengths in the linear flow direction network
                  immediately downstream of this network extending to the next
                  barrier downstream or downstream-most point of the network,
                  excluding all lengths within altered waterbodies.
                </InfoTooltip>
              </Box>
            </Box>
            <Box
              sx={{
                fontWeight:
                  mainstemGainMilesSide === 'upstream' ? 'bold' : 'inherited',
              }}
            >
              {formatNumber(totalmainstemupstreammiles, 2, true)}
            </Box>
            <Box
              sx={{
                fontWeight:
                  mainstemGainMilesSide === 'downstream' ? 'bold' : 'inherited',
              }}
            >
              {formatNumber(freemainstemdownstreammiles, 2, true)}
            </Box>
          </Row>

          <Row sx={{ px: '0.5rem' }}>
            <Box>
              <Text sx={{ display: 'inline' }}>Perennial miles</Text>
              <Box sx={{ display: 'inline-block' }}>
                <InfoTooltip>
                  Total perennial mainstem miles upstream is the sum of all
                  perennial reach lengths in the upstream mainstem network.
                  Perennial reaches are all those that are not specifically
                  identified as ephemeral or intermittent. Perennial reaches are
                  not necessarily contiguous.
                  <br />
                  <br />
                  Total perennial miles downstream is the sum of all perennial
                  reach lengths in the linear flow direction network immediately
                  downstream of this network, excluding all lengths within
                  altered waterbodies.
                </InfoTooltip>
              </Box>
            </Box>
            <Box
              sx={{
                fontWeight:
                  perennialMainstemGainMilesSide === 'upstream'
                    ? 'bold'
                    : 'inherited',
              }}
            >
              {formatNumber(perennialmainstemupstreammiles, 2, true)}
            </Box>
            <Box
              sx={{
                fontWeight:
                  perennialMainstemGainMilesSide === 'downstream'
                    ? 'bold'
                    : 'inherited',
              }}
            >
              {formatNumber(freeperennialmainstemdownstreammiles, 2, true)}
            </Box>
          </Row>

          <Row sx={{ px: '0.5rem' }}>
            <Box>
              <Text sx={{ display: 'inline' }}>Intermittent miles</Text>

              <Box sx={{ display: 'inline-block' }}>
                <InfoTooltip>
                  Total ephemeral and intermittent mainstem miles upstream is
                  the sum of all ephemeral and intermittent reach lengths in the
                  upstream mainstem network.
                  <br />
                  <br />
                  Total ephemeral and intermittent miles downstream is the sum
                  of all ephemeral and intermittent reach lengths in the
                  downstream mainstem network in the linear flow direction
                  immediately downstream of this network, excluding all lengths
                  within altered waterbodies.
                </InfoTooltip>
              </Box>
            </Box>
            <Box>
              {formatNumber(intermittentmainstemupstreammiles, 2, true)}
            </Box>
            <Box>
              {formatNumber(freeintermittentmainstemdownstreammiles, 2, true)}
            </Box>
          </Row>

          <Row sx={{ px: '0.5rem' }}>
            <Box>
              <Text sx={{ display: 'inline' }}>Altered miles</Text>
              <Box sx={{ display: 'inline-block' }}>
                <InfoTooltip>
                  Total altered mainstem miles upstream is the sum of all reach
                  lengths specifically identified as altered (canal / ditch,
                  within reservoir, or other channel alteration) within the
                  upstream mainstem network.
                  <br />
                  <br />
                  Total altered miles downstream is the sum of all altered reach
                  lengths in the downstream mainstem network in the linear flow
                  direction immediately downstream of this network, excluding
                  all lengths within altered waterbodies.
                </InfoTooltip>
              </Box>
            </Box>
            <Box>{formatNumber(alteredmainstemupstreammiles, 2, true)}</Box>
            <Box>
              {formatNumber(freealteredmainstemdownstreammiles, 2, true)}
            </Box>
          </Row>

          <Row sx={{ px: '0.5rem' }}>
            <Box>
              <Text sx={{ display: 'inline' }}>Unaltered miles</Text>

              <Box sx={{ display: 'inline-block' }}>
                <InfoTooltip>
                  Total unaltered mainstem miles upstream is the sum of all
                  reach lengths not specifically identified as altered (canal /
                  ditch, within reservoir, or other channel alteration) within
                  the upstream mainstem network.
                  <br />
                  <br />
                  Total unaltered miles downstream is the sum of all unaltered
                  reach lengths in the downstream mainstem network in the linear
                  flow direction immediately downstream of this network,
                  excluding all lengths within altered waterbodies.
                </InfoTooltip>
              </Box>
            </Box>
            <Box>{formatNumber(unalteredmainstemupstreammiles, 2, true)}</Box>
            <Box>
              {formatNumber(freeunalteredmainstemdownstreammiles, 2, true)}
            </Box>
          </Row>
        </Table>

        {barrierType !== 'waterfalls' ? (
          <Table
            columns="11rem 1fr 1fr"
            sx={{
              mt: '0.25rem',
              pt: '0.25rem',
              fontSize,
              borderTop: '2px solid',
              borderTopColor: 'grey.4',
            }}
          >
            <Row sx={{ px: '0.5rem' }}>
              <Box>
                <Text sx={{ display: 'inline', fontWeight: 'bold' }}>
                  Total mainstem miles gained
                </Text>
                <Box sx={{ display: 'inline-block' }}>
                  <InfoTooltip>
                    The total mainstem miles that{' '}
                    {removed ? 'were' : 'could be'} gained by removing this
                    barrier is the lesser of the upstream mainstem network miles
                    or free-flowing downstream mainstem network miles.
                  </InfoTooltip>
                </Box>
              </Box>
              <Box
                sx={
                  mainstemGainMilesSide === 'upstream'
                    ? activeSideCSS
                    : inactiveSideCSS
                }
              >
                {formatNumber(totalmainstemupstreammiles, 2, true)}
                {alwaysUseUpstream ? <sup>*</sup> : null}
              </Box>
              <Box
                sx={
                  mainstemGainMilesSide === 'downstream'
                    ? activeSideCSS
                    : inactiveSideCSS
                }
              >
                {formatNumber(freemainstemdownstreammiles, 2, true)}
              </Box>
            </Row>
            <Row sx={{ px: '0.5rem' }}>
              <Box>
                <Text sx={{ fontWeight: 'bold', display: 'inline' }}>
                  Perennial mainstem miles gained
                </Text>
                <Box sx={{ display: 'inline-block' }}>
                  <InfoTooltip>
                    The total perennial mainstem miles that{' '}
                    {removed ? 'were' : 'could be'} gained by removing this
                    barrier is the lesser of the upstream perennial mainstem
                    network miles or free-flowing downstream mainstem network
                    perennial miles.
                  </InfoTooltip>
                </Box>
              </Box>
              <Box
                sx={
                  perennialMainstemGainMilesSide === 'upstream'
                    ? activeSideCSS
                    : inactiveSideCSS
                }
              >
                {formatNumber(perennialmainstemupstreammiles, 2, true)}
                {alwaysUseUpstream ? <sup>*</sup> : null}
              </Box>
              <Box
                sx={
                  perennialMainstemGainMilesSide === 'downstream'
                    ? activeSideCSS
                    : inactiveSideCSS
                }
              >
                {formatNumber(freeperennialmainstemdownstreammiles, 2, true)}
              </Box>
            </Row>
          </Table>
        ) : null}

        <Text variant="help" sx={{ fontSize: 0, px: '0.5rem', mt: '2rem' }}>
          {barrierType !== 'waterfalls' && alwaysUseUpstream ? (
            <>
              <sup>*</sup>upstream miles are used because the downstream network
              flows into the {flowstogreatlakes === 1 ? 'Great Lakes' : 'ocean'}{' '}
              and there are no barriers downstream.
              <br />
              <br />
            </>
          ) : null}
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
            ? `, including any that were present at the time this
                ${barrierTypeLabel} was removed, with the exception of those
                directly upstream that were removed in the same year as this barrier.
                All barriers removed prior to 2000 or where the year they were
                removed was unknown were lumped together for this analysis`
            : null}
          .
        </Text>
      </Entry>
      {totalmainstemupstreammiles > 0 ? (
        <>
          <Entry>
            <Field label="Percent of the upstream network in unaltered stream channels">
              <Text
                sx={{
                  fontSize: 1,
                  fontWeight: 'bold',
                }}
              >
                {formatPercent(percentUnaltered)}%
              </Text>
            </Field>
          </Entry>
          <Entry>
            <Field
              label={
                barrierType === 'waterfalls'
                  ? 'Number of mainstem size classes upstream'
                  : `Number of mainstem size classes that ${
                      removed ? 'were' : 'could be'
                    } gained by removing this barrier`
              }
            >
              <Text
                sx={{
                  fontSize: 1,
                  fontWeight: mainstemsizeclasses > 0 ? 'bold' : 'inherit',
                }}
              >
                {mainstemsizeclasses}
              </Text>
            </Field>
          </Entry>
        </>
      ) : null}
    </Box>
  )
}

MainstemNetworkInfo.propTypes = {
  ...MainstemNetworkPropTypeStub,
  fontSize: PropTypes.oneOfType([PropTypes.string, PropTypes.number]),
  headerFontSize: PropTypes.oneOfType([PropTypes.string, PropTypes.number]),
  barrierType: PropTypes.string.isRequired,
  networkType: PropTypes.string.isRequired,
  removed: PropTypes.bool,
}

MainstemNetworkInfo.defaultProps = {
  ...MainstemNetworkDefaultProps,
  fontSize: 1,
  headerFontSize: 0,
  removed: false,
}

export default MainstemNetworkInfo
