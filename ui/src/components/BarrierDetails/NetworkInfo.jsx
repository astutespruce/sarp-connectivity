import React from 'react'
import PropTypes from 'prop-types'
import { Box, Text } from 'theme-ui'

import { Table, Row } from 'components/Table'
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

  const percentAltered = totalupstreammiles
    ? (100 * alteredupstreammiles) / totalupstreammiles
    : 0

  return (
    <Box {...props}>
      <Entry sx={{ pb: '1rem' }}>
        <Table sx={{ fontSize: 1 }} columns="11rem 1fr 1fr">
          <Row>
            <Box />
            <Box sx={{ fontSize: 0 }}>
              <b>Upstream</b>
            </Box>
            <Box sx={{ fontSize: 0 }}>
              <b>Downstream</b>
              <br />
              <Text sx={{ fontSize: 0, color: 'grey.7' }}>
                free-flowing miles only
              </Text>
            </Box>
          </Row>

          <Row>
            <Box>Total miles</Box>
            <Box
              sx={{
                fontWeight: gainMilesSide === 'upstream' ? 'bold' : 'inherited',
              }}
            >
              {formatNumber(totalupstreammiles)}
            </Box>
            <Box
              sx={{
                fontWeight:
                  gainMilesSide === 'downstream' ? 'bold' : 'inherited',
              }}
            >
              {formatNumber(freedownstreammiles)}
            </Box>
          </Row>

          <Row>
            <Box>Perennial miles</Box>
            <Box
              sx={{
                fontWeight: gainMilesSide === 'upstream' ? 'bold' : 'inherited',
              }}
            >
              {formatNumber(perennialupstreammiles)}
            </Box>
            <Box
              sx={{
                fontWeight:
                  gainMilesSide === 'downstream' ? 'bold' : 'inherited',
              }}
            >
              {formatNumber(freeperennialdownstreammiles)}
            </Box>
          </Row>

          <Row>
            <Box>Altered miles</Box>
            <Box>{formatNumber(alteredupstreammiles)}</Box>
            <Box>{formatNumber(freealtereddownstreammiles)}</Box>
          </Row>

          <Row>
            <Box>Unaltered miles</Box>
            <Box>{formatNumber(unalteredupstreammiles)}</Box>
            <Box>{formatNumber(freeunaltereddownstreammiles)}</Box>
          </Row>
        </Table>

        {barrierType !== 'waterfalls' ? (
          <Table
            columns="11rem 1fr 1fr"
            sx={{
              mt: '0.25rem',
              pt: '0.25rem',
              fontSize: 1,
              borderTop: '3px solid',
              borderTopColor: 'grey.2',
            }}
          >
            <Row>
              <Box>
                <b>Total miles gained</b>
              </Box>
              <Box
                sx={
                  gainMilesSide === 'upstream' ? activeSideCSS : inactiveSideCSS
                }
              >
                {formatNumber(totalupstreammiles)}
              </Box>
              <Box
                sx={
                  gainMilesSide === 'downstream'
                    ? activeSideCSS
                    : inactiveSideCSS
                }
              >
                {formatNumber(freedownstreammiles)}
              </Box>
            </Row>
            <Row>
              <Box>
                <b>Perennial miles gained</b>
              </Box>
              <Box
                sx={
                  perennialGainMilesSide === 'upstream'
                    ? activeSideCSS
                    : inactiveSideCSS
                }
              >
                {formatNumber(perennialupstreammiles)}
              </Box>
              <Box
                sx={
                  perennialGainMilesSide === 'downstream'
                    ? activeSideCSS
                    : inactiveSideCSS
                }
              >
                {formatNumber(freeperennialdownstreammiles)}
              </Box>
            </Row>
          </Table>
        ) : null}
      </Entry>

      {totalupstreammiles > 0 ? (
        <Entry>
          <b>{formatPercent(percentAltered)}%</b> of the upstream network is in
          stream channels altered from natural conditions (coded as canals or
          ditches).
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
