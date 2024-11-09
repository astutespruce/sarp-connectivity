import React from 'react'
import PropTypes from 'prop-types'
import { Box, Text } from 'theme-ui'

import { barrierTypeLabelSingular } from 'config'
import { Table, Row } from 'components/Table'
import { InfoTooltip } from 'components/Tooltip'
import { Entry, Field } from 'components/Sidebar'
import { formatNumber, formatPercent } from 'util/format'

const activeSideCSS = {
  fontWeight: 'bold',
}
const inactiveSideCSS = {
  visibility: 'hidden',
}

const MainstemNetworkInfo = ({
  barrierType,
  networkType,
  totalupstreammainstemmiles,
  perennialupstreammainstemmiles,
  alteredupstreammainstemmiles,
  unalteredupstreammainstemmiles,
  freelineardownstreammiles,
  freeperenniallineardownstreammiles,
  freealteredlineardownstreammiles,
  freeunalteredlineardownstreammiles,
  mainstemsizeclasses,
  fontSize,
  headerFontSize,
  removed,
  flowstoocean,
  flowstogreatlakes,
  totaldownstreamdams,
  totaldownstreamsmallbarriers,
  totaldownstreamwaterfalls,
  ...props
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
    totalupstreammainstemmiles,
    freelineardownstreammiles
  )
  const mainstemGainMilesSide =
    alwaysUseUpstream || mainstemGainMiles === totalupstreammainstemmiles
      ? 'upstream'
      : 'downstream'

  const perennialMainstemGainMiles = Math.min(
    perennialupstreammainstemmiles,
    freeperenniallineardownstreammiles
  )
  const perennialMainstemGainMilesSide =
    alwaysUseUpstream ||
    perennialMainstemGainMiles === perennialupstreammainstemmiles
      ? 'upstream'
      : 'downstream'

  const intermittentupstreammainstemmiles =
    totalupstreammainstemmiles - perennialupstreammainstemmiles
  const freeintermittentlineardownstreammiles =
    freelineardownstreammiles - freeperenniallineardownstreammiles

  const percentAltered = totalupstreammainstemmiles
    ? (100 * alteredupstreammainstemmiles) / totalupstreammainstemmiles
    : 0

  return (
    <Box {...props}>
      <Text variant="help" sx={{ fontSize: 0 }}>
        <Text variant="help" sx={{ fontSize: 0, mx: '0.5rem', mb: '1rem' }}>
          Upstream mainstem networks include the stream reaches upstream that
          are the same stream order as the one associated with this barrier
          (excludes smaller tributaries) with at least 1 square mile of drainage
          area. Downstream mainstem networks are based on the linear flow
          direction network from this barrier to the next barrier downstream or
          downstream-most point on that network (does not include any
          tributaries).
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
              {formatNumber(totalupstreammainstemmiles, 2, true)}
            </Box>
            <Box
              sx={{
                fontWeight:
                  mainstemGainMilesSide === 'downstream' ? 'bold' : 'inherited',
              }}
            >
              {formatNumber(freelineardownstreammiles, 2, true)}
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
              {formatNumber(perennialupstreammainstemmiles, 2, true)}
            </Box>
            <Box
              sx={{
                fontWeight:
                  perennialMainstemGainMilesSide === 'downstream'
                    ? 'bold'
                    : 'inherited',
              }}
            >
              {formatNumber(freeperenniallineardownstreammiles, 2, true)}
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
                  of all ephemeral and intermittent reach lengths in the linear
                  flow direction network immediately downstream of this network,
                  excluding all lengths within altered waterbodies.
                </InfoTooltip>
              </Box>
            </Box>
            <Box>
              {formatNumber(intermittentupstreammainstemmiles, 2, true)}
            </Box>
            <Box>
              {formatNumber(freeintermittentlineardownstreammiles, 2, true)}
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
                  lengths in the linear flow direction network immediately
                  downstream of this network, excluding all lengths within
                  altered waterbodies.
                </InfoTooltip>
              </Box>
            </Box>
            <Box>{formatNumber(alteredupstreammainstemmiles, 2, true)}</Box>
            <Box>{formatNumber(freealteredlineardownstreammiles, 2, true)}</Box>
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
                  reach lengths in the linear flow direction network immediately
                  downstream of this network, excluding all lengths within
                  altered waterbodies.
                </InfoTooltip>
              </Box>
            </Box>
            <Box>{formatNumber(unalteredupstreammainstemmiles, 2, true)}</Box>
            <Box>
              {formatNumber(freeunalteredlineardownstreammiles, 2, true)}
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
                    or downstream linear flow direction network miles.
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
                {formatNumber(totalupstreammainstemmiles, 2, true)}
                {alwaysUseUpstream ? <sup>*</sup> : null}
              </Box>
              <Box
                sx={
                  mainstemGainMilesSide === 'downstream'
                    ? activeSideCSS
                    : inactiveSideCSS
                }
              >
                {formatNumber(freelineardownstreammiles, 2, true)}
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
                    network miles or downstream linear flow direction network
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
                {formatNumber(perennialupstreammainstemmiles, 2, true)}
                {alwaysUseUpstream ? <sup>*</sup> : null}
              </Box>
              <Box
                sx={
                  perennialMainstemGainMilesSide === 'downstream'
                    ? activeSideCSS
                    : inactiveSideCSS
                }
              >
                {formatNumber(freeperenniallineardownstreammiles, 2, true)}
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
      {totalupstreammainstemmiles > 0 ? (
        <>
          <Entry>
            <Field label="Percent of the upstream network in altered stream channels">
              <Text
                sx={{
                  fontSize: 1,
                  fontWeight: 'bold',
                }}
              >
                {formatPercent(percentAltered)}%
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
  fontSize: PropTypes.oneOfType([PropTypes.string, PropTypes.number]),
  headerFontSize: PropTypes.oneOfType([PropTypes.string, PropTypes.number]),
  barrierType: PropTypes.string.isRequired,
  networkType: PropTypes.string.isRequired,
  totalupstreammainstemmiles: PropTypes.number,
  perennialupstreammainstemmiles: PropTypes.number,
  alteredupstreammainstemmiles: PropTypes.number,
  unalteredupstreammainstemmiles: PropTypes.number,
  mainstemsizeclasses: PropTypes.number,
  freelineardownstreammiles: PropTypes.number,
  freeperenniallineardownstreammiles: PropTypes.number,
  freealteredlineardownstreammiles: PropTypes.number,
  freeunalteredlineardownstreammiles: PropTypes.number,
  removed: PropTypes.bool,
  flowstoocean: PropTypes.number,
  flowstogreatlakes: PropTypes.number,
  totaldownstreamdams: PropTypes.number,
  totaldownstreamsmallbarriers: PropTypes.number,
  totaldownstreamwaterfalls: PropTypes.number,
}

MainstemNetworkInfo.defaultProps = {
  fontSize: 1,
  headerFontSize: 0,
  totalupstreammainstemmiles: 0,
  perennialupstreammainstemmiles: 0,
  alteredupstreammainstemmiles: 0,
  unalteredupstreammainstemmiles: 0,
  mainstemsizeclasses: 0,
  freelineardownstreammiles: 0,
  freeperenniallineardownstreammiles: 0,
  freealteredlineardownstreammiles: 0,
  freeunalteredlineardownstreammiles: 0,
  removed: false,
  flowstoocean: 0,
  flowstogreatlakes: 0,
  totaldownstreamdams: 0,
  totaldownstreamsmallbarriers: 0,
  totaldownstreamwaterfalls: 0,
}

export default MainstemNetworkInfo
