import React from 'react'
import PropTypes from 'prop-types'
import { Box, Paragraph, Text } from 'theme-ui'

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

const NetworkInfo = ({
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
  fontSize,
  headerFontSize,
  invasive,
  unranked,
  removed,
  ...props
}) => {
  const barrierTypeLabel = barrierTypeLabelSingular[barrierType]

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

  return (
    <Box {...props}>
      <Entry sx={{ pb: '.5rem', mx: '-0.5rem' }}>
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
                  Total miles upstream is the sum of all river and stream
                  lengths in the upstream functional network.
                  <br />
                  <br />
                  Total miles downstream is the sum of all river and stream
                  lengths in the functional network immediately downstream of
                  this network, excluding all lengths within waterbodies.
                </InfoTooltip>
              </Box>
            </Box>
            <Box
              sx={{
                fontWeight: gainMilesSide === 'upstream' ? 'bold' : 'inherited',
              }}
            >
              {formatNumber(totalupstreammiles, 2, true)}
            </Box>
            <Box
              sx={{
                fontWeight:
                  gainMilesSide === 'downstream' ? 'bold' : 'inherited',
              }}
            >
              {formatNumber(freedownstreammiles, 2, true)}
            </Box>
          </Row>

          <Row sx={{ px: '0.5rem' }}>
            <Box>
              <Text sx={{ display: 'inline' }}>Perennial miles</Text>
              <Box sx={{ display: 'inline-block' }}>
                <InfoTooltip>
                  Total perennial miles upstream is the sum of all perennial
                  reach lengths in the upstream functional network. Perennial
                  reaches are all those that are not specifically identified as
                  ephemeral or intermittent. Perennial reaches are not
                  necessarily contiguous.
                  <br />
                  <br />
                  Total perennial miles downstream is the sum of all perennial
                  reach lengths in the functional network immediately downstream
                  of this network, excluding all lengths within waterbodies.
                </InfoTooltip>
              </Box>
            </Box>
            <Box
              sx={{
                fontWeight: gainMilesSide === 'upstream' ? 'bold' : 'inherited',
              }}
            >
              {formatNumber(perennialupstreammiles, 2, true)}
            </Box>
            <Box
              sx={{
                fontWeight:
                  gainMilesSide === 'downstream' ? 'bold' : 'inherited',
              }}
            >
              {formatNumber(freeperennialdownstreammiles, 2, true)}
            </Box>
          </Row>

          <Row sx={{ px: '0.5rem' }}>
            <Box>
              <Text sx={{ display: 'inline' }}>Intermittent miles</Text>

              <Box sx={{ display: 'inline-block' }}>
                <InfoTooltip>
                  Total ephemeral and intermittent miles upstream is the sum of
                  all ephemeral and intermittent reach lengths in the upstream
                  functional network.
                  <br />
                  <br />
                  Total ephemeral and intermittent miles downstream is the sum
                  of all ephemeral and intermittent reach lengths in the
                  functional network immediately downstream of this network,
                  excluding all lengths within waterbodies.
                </InfoTooltip>
              </Box>
            </Box>
            <Box
              sx={{
                fontWeight: gainMilesSide === 'upstream' ? 'bold' : 'inherited',
              }}
            >
              {formatNumber(intermittentupstreammiles, 2, true)}
            </Box>
            <Box
              sx={{
                fontWeight:
                  gainMilesSide === 'downstream' ? 'bold' : 'inherited',
              }}
            >
              {formatNumber(freeintermittentdownstreammiles, 2, true)}
            </Box>
          </Row>

          <Row sx={{ px: '0.5rem' }}>
            <Box>
              <Text sx={{ display: 'inline' }}>Altered miles</Text>
              <Box sx={{ display: 'inline-block' }}>
                <InfoTooltip>
                  Total altered miles upstream is the sum of all reach lengths
                  specifically identified as altered (canal / ditch, within
                  reservoir, or other channel alteration).
                  <br />
                  <br />
                  Total altered miles downstream is the sum of all altered reach
                  lengths in the functional network immediately downstream of
                  this network, excluding all lengths within waterbodies.
                </InfoTooltip>
              </Box>
            </Box>
            <Box>{formatNumber(alteredupstreammiles, 2, true)}</Box>
            <Box>{formatNumber(freealtereddownstreammiles, 2, true)}</Box>
          </Row>

          <Row sx={{ px: '0.5rem' }}>
            <Box>
              <Text sx={{ display: 'inline' }}>Unaltered miles</Text>

              <Box sx={{ display: 'inline-block' }}>
                <InfoTooltip>
                  Total unaltered miles upstream is the sum of all reach lengths
                  not specifically identified as altered (canal / ditch, within
                  reservoir, or other channel alteration).
                  <br />
                  <br />
                  Total unaltered miles downstream is the sum of all unaltered
                  reach lengths in the functional network immediately downstream
                  of this network, excluding all lengths within waterbodies.
                </InfoTooltip>
              </Box>
            </Box>
            <Box>{formatNumber(unalteredupstreammiles, 2, true)}</Box>
            <Box>{formatNumber(freeunaltereddownstreammiles, 2, true)}</Box>
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
                  Total miles gained
                </Text>
                <Box sx={{ display: 'inline-block' }}>
                  <InfoTooltip>
                    The total miles that {removed ? 'were' : 'could be'} gained
                    by removing this barrier is the lesser of the upstream or
                    downstream total functional network miles.
                  </InfoTooltip>
                </Box>
              </Box>
              <Box
                sx={
                  gainMilesSide === 'upstream' ? activeSideCSS : inactiveSideCSS
                }
              >
                {formatNumber(totalupstreammiles, 2, true)}
              </Box>
              <Box
                sx={
                  gainMilesSide === 'downstream'
                    ? activeSideCSS
                    : inactiveSideCSS
                }
              >
                {formatNumber(freedownstreammiles, 2, true)}
              </Box>
            </Row>
            <Row sx={{ px: '0.5rem' }}>
              <Box>
                <Text sx={{ fontWeight: 'bold', display: 'inline' }}>
                  Perennial miles gained
                </Text>
                <Box sx={{ display: 'inline-block' }}>
                  <InfoTooltip>
                    The total perennial miles that{' '}
                    {removed ? 'were' : 'could be'} gained by removing this
                    barrier is the lesser of the upstream or downstream
                    perennial miles.
                  </InfoTooltip>
                </Box>
              </Box>
              <Box
                sx={
                  perennialGainMilesSide === 'upstream'
                    ? activeSideCSS
                    : inactiveSideCSS
                }
              >
                {formatNumber(perennialupstreammiles, 2, true)}
              </Box>
              <Box
                sx={
                  perennialGainMilesSide === 'downstream'
                    ? activeSideCSS
                    : inactiveSideCSS
                }
              >
                {formatNumber(freeperennialdownstreammiles, 2, true)}
              </Box>
            </Row>
          </Table>
        ) : null}

        <Text variant="help" sx={{ fontSize: 0, px: '0.5rem', mt: '2rem' }}>
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

      {totalupstreammiles > 0 ? (
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
      ) : null}

      <Entry>
        <Field
          label={
            barrierType === 'waterfalls'
              ? 'Number of size classes upstream'
              : `Number of size classes that ${
                  removed ? 'were' : 'could be'
                } gained by removing this barrier`
          }
        >
          <Text
            sx={{
              fontSize: 1,
              fontWeight: sizeclasses > 0 ? 'bold' : 'inherit',
            }}
          >
            {sizeclasses}
          </Text>
        </Field>
      </Entry>
      <Entry>
        <Field label="Percent of upstream floodplain composed of natural landcover">
          <Text
            sx={{
              fontSize: 1,
              fontWeight: 'bold',
            }}
          >
            {formatNumber(landcover, 0)}%
          </Text>
        </Field>
      </Entry>

      {invasive ? (
        <Entry>
          <Paragraph variant="help" sx={{ mt: '1rem', fontSize: 0 }}>
            Note: this {barrierTypeLabel} is identified as a beneficial to
            restricting the movement of invasive species and is not ranked.
          </Paragraph>
        </Entry>
      ) : null}

      {unranked && !invasive ? (
        <Entry>
          <Paragraph variant="help" sx={{ mt: '1rem', fontSize: 0 }}>
            Note: this {barrierTypeLabel} excluded from ranking based on field
            reconnaissance, manual review of aerial imagery, or other
            information about this {barrierTypeLabel}.
          </Paragraph>
        </Entry>
      ) : null}
    </Box>
  )
}

NetworkInfo.propTypes = {
  fontSize: PropTypes.oneOfType([PropTypes.string, PropTypes.number]),
  headerFontSize: PropTypes.oneOfType([PropTypes.string, PropTypes.number]),
  barrierType: PropTypes.string.isRequired,
  networkType: PropTypes.string.isRequired,
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
}

NetworkInfo.defaultProps = {
  fontSize: 1,
  headerFontSize: 0,
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
}

export default NetworkInfo
