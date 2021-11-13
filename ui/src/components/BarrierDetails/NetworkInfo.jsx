import React from 'react'
import PropTypes from 'prop-types'
import { Box, Text } from 'theme-ui'

import { Table, Row } from 'components/Table'
import { InfoTooltip } from 'components/Tooltip'
import { Entry } from 'components/Sidebar'
import { formatNumber, formatPercent } from 'util/format'

const activeSideCSS = {
  fontWeight: 'bold',
}
const inactiveSideCSS = {
  visibility: 'hidden',
}

const NetworkInfo = ({
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
  fontSize,
  headerFontSize,
  ...props
}) => {
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
      <Entry sx={{ pb: '1rem' }}>
        <Table sx={{ fontSize }} columns="11rem 1fr 1fr">
          <Row>
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

          <Row>
            <Box>
              <Text sx={{ display: 'inline' }}>Total miles</Text>
              <InfoTooltip>
                Total miles upstream is the sum of all river and stream lengths
                in the upstream functional network.
                <br />
                <br />
                Total miles downstream is the sum of all river and stream
                lengths in the functional network immediately downstream of this
                network, excluding all lengths within waterbodies.
              </InfoTooltip>
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

          <Row>
            <Box>
              <Text sx={{ display: 'inline' }}>Perennial miles</Text>
              <InfoTooltip>
                Total perennial miles upstream is the sum of all perennial reach
                lengths in the upstream functional network. Perennial reaches
                are all those that are not specifically identified as ephemeral
                or intermittent. Perennial reaches are not necessarily
                contiguous.
                <br />
                <br />
                Total perennial miles downstream is the sum of all perennial
                reach lengths in the functional network immediately downstream
                of this network, excluding all lengths within waterbodies.
              </InfoTooltip>
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

          <Row>
            <Box>
              <Text sx={{ display: 'inline' }}>
                Intermittent / ephemeral miles
              </Text>
              <InfoTooltip>
                Total ephemeral and intermittent miles upstream is the sum of
                all ephemeral and intermittent reach lengths in the upstream
                functional network.
                <br />
                <br />
                Total ephemeral and intermittent miles downstream is the sum of
                all ephemeral and intermittent reach lengths in the functional
                network immediately downstream of this network, excluding all
                lengths within waterbodies.
              </InfoTooltip>
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

          <Row>
            <Box>
              <Text sx={{ display: 'inline' }}>Altered miles</Text>
              <InfoTooltip>
                Total altered miles upstream is the sum of all reach lengths
                specifically identified as altered (canal / ditch).
                <br />
                <br />
                Total altered miles downstream is the sum of all altered reach
                lengths in the functional network immediately downstream of this
                network, excluding all lengths within waterbodies.
              </InfoTooltip>
            </Box>
            <Box>{formatNumber(alteredupstreammiles, 2, true)}</Box>
            <Box>{formatNumber(freealtereddownstreammiles, 2, true)}</Box>
          </Row>

          <Row>
            <Box>
              <Text sx={{ display: 'inline' }}>Unaltered miles</Text>

              <InfoTooltip>
                Total unaltered miles upstream is the sum of all reach lengths
                not specifically identified as altered (canal / ditch).
                <br />
                <br />
                Total unaltered miles downstream is the sum of all unaltered
                reach lengths in the functional network immediately downstream
                of this network, excluding all lengths within waterbodies.
              </InfoTooltip>
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
              borderTop: '3px solid',
              borderTopColor: 'grey.2',
            }}
          >
            <Row>
              <Box>
                <Text sx={{ fontWeight: 'bold', display: 'inline' }}>
                  Total miles gained
                </Text>
                <InfoTooltip>
                  The total miles that could be gained by removing this barrier
                  is the lesser of the upstream or downstream total functional
                  network miles.
                </InfoTooltip>
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
            <Row>
              <Box>
                <Text sx={{ fontWeight: 'bold', display: 'inline' }}>
                  Perennial miles gained
                </Text>
                <InfoTooltip>
                  The total perennial miles that could be gained by removing
                  this barrier is the lesser of the upstream or downstream
                  perennial miles.
                </InfoTooltip>
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
      </Entry>

      {totalupstreammiles > 0 ? (
        <Entry>
          <b>{formatPercent(percentAltered)}%</b> of the upstream network is in
          altered stream channels (coded as canals / ditches)
        </Entry>
      ) : null}

      {barrierType === 'waterfalls' ? (
        <Entry>
          <b>{sizeclasses}</b> river size{' '}
          {sizeclasses === 1 ? 'class is' : 'classes are'} upstream of this
          waterfall
        </Entry>
      ) : (
        <Entry>
          <b>{sizeclasses}</b> river size{' '}
          {sizeclasses === 1 ? 'class' : 'classes'} could be gained by removing
          this barrier
        </Entry>
      )}
      <Entry>
        <b>{formatNumber(landcover, 0)}%</b> of the upstream floodplain is
        composed of natural landcover
      </Entry>
    </Box>
  )
}

NetworkInfo.propTypes = {
  fontSize: PropTypes.oneOfType([PropTypes.string, PropTypes.number]),
  headerFontSize: PropTypes.oneOfType([PropTypes.string, PropTypes.number]),
  barrierType: PropTypes.string.isRequired,
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
}

export default NetworkInfo
