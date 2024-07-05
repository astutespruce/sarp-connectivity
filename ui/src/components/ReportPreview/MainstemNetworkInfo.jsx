import React from 'react'
import PropTypes from 'prop-types'
import { Box, Heading, Paragraph } from 'theme-ui'

import { Table, Row } from 'components/Table'
import { barrierTypeLabelSingular } from 'config'
import { formatNumber } from 'util/format'

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
  removed,
  flowstoocean,
  flowstogreatlakes,
  totaldownstreamdams,
  totaldownstreamsmallbarriers,
  totaldownstreamwaterfalls,
  sx,
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

  return (
    <Box sx={sx}>
      <Heading as="h3">Mainstem network information</Heading>

      <Paragraph variant="help" sx={{ fontSize: 0 }}>
        Upstream mainstem networks include the stream reaches upstream that are
        the same stream order as the one associated with this barrier (excludes
        smaller tributaries) with at least 1 square mile of drainage area.
        Downstream mainstem networks are based on the linear flow direction
        network from this barrier to the next barrier downstream or
        downstream-most point on that network (does not include any
        tributaries).
      </Paragraph>

      <Box sx={{ mt: '1rem' }}>
        <Table
          columns="16rem 1fr 1fr"
          sx={{
            mt: '1rem',
            '> div:not(:first-of-type)': {
              pt: '0.5rem',
            },
          }}
        >
          <Row>
            <Box />
            <Box>
              <b>upstream network</b>
            </Box>
            <Box>
              <b>downstream network</b>
            </Box>
          </Row>

          <Row>
            <Box>Total miles</Box>
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

          <Row>
            <Box>Perennial miles</Box>
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

          <Row>
            <Box>Ephemeral / intermittent miles</Box>
            <Box>
              {formatNumber(intermittentupstreammainstemmiles, 2, true)}
            </Box>
            <Box>
              {formatNumber(freeintermittentlineardownstreammiles, 2, true)}
            </Box>
          </Row>

          <Row>
            <Box>Altered miles</Box>
            <Box>{formatNumber(alteredupstreammainstemmiles, 2, true)}</Box>
            <Box>{formatNumber(freealteredlineardownstreammiles, 2, true)}</Box>
          </Row>

          <Row>
            <Box>Unaltered miles</Box>
            <Box>{formatNumber(unalteredupstreammainstemmiles, 2, true)}</Box>
            <Box>
              {formatNumber(freeunalteredlineardownstreammiles, 2, true)}
            </Box>
          </Row>
        </Table>
      </Box>

      <Paragraph variant="help" sx={{ mt: '2rem', fontSize: 0 }}>
        {alwaysUseUpstream ? (
          <>
            Note: upstream miles are used because the downstream network flows
            into the {flowstogreatlakes === 1 ? 'Great Lakes' : 'ocean'} and
            there are no barriers downstream.
            <br />
            <br />
          </>
        ) : null}
        Note: Statistics are based on aquatic networks cut by{' '}
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
            ${barrierTypeLabel} was removed, with the exception of those directly
            upstream that were removed in the same year as this barrier.
            All barriers removed prior to 2000 or where the year they were removed
            was unknown were lumped together for this analysis`
          : null}
        .
      </Paragraph>
    </Box>
  )
}

MainstemNetworkInfo.propTypes = {
  barrierType: PropTypes.string.isRequired,
  networkType: PropTypes.string.isRequired,
  totalupstreammainstemmiles: PropTypes.number,
  perennialupstreammainstemmiles: PropTypes.number,
  alteredupstreammainstemmiles: PropTypes.number,
  unalteredupstreammainstemmiles: PropTypes.number,
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
  sx: PropTypes.object,
}

MainstemNetworkInfo.defaultProps = {
  totalupstreammainstemmiles: 0,
  perennialupstreammainstemmiles: 0,
  alteredupstreammainstemmiles: 0,
  unalteredupstreammainstemmiles: 0,
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
  sx: null,
}

export default MainstemNetworkInfo
