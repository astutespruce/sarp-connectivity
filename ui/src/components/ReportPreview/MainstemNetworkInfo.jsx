import React from 'react'
import PropTypes from 'prop-types'
import { Box, Grid, Heading, Paragraph } from 'theme-ui'

import {
  MainstemNetworkPropTypeStub,
  MainstemNetworkDefaultProps,
  LinearDownstreamNetworkPropTypeStub,
  LinearDownstreamNetworkDefaultProps,
} from 'components/BarrierDetails/proptypes'
import { Table, Row } from 'components/Table'
import { barrierTypeLabelSingular } from 'config'
import { formatNumber, formatPercent } from 'util/format'

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
    <Box sx={sx}>
      <Heading as="h3">Mainstem network information</Heading>

      <Paragraph variant="help" sx={{ fontSize: 0 }}>
        Upstream mainstem networks include the stream reaches upstream that are
        the same stream order as the one associated with this barrier (excludes
        smaller tributaries) with at least 1 square mile of drainage area.
        Downstream mainstem networks are based on the linear flow direction
        through the same stream order to the next barrier downstream, a change
        in stream order, or the downstream-most point on the network.
      </Paragraph>

      <Grid
        columns={totalmainstemupstreammiles > 0 ? 3 : 2}
        gap={0}
        sx={{
          mt: '1rem',
          '&>div': {
            py: '0.5em',
          },
          '&>div + div': {
            ml: '1rem',
            pl: '1rem',
            borderLeft: '1px solid',
            borderLeftColor: 'grey.3',
          },
        }}
      >
        <Box>
          <b>{formatNumber(mainstemGainMiles, 2, true)} total miles</b>{' '}
          {removed ? 'were' : 'could be'} gained by removing this{' '}
          {barrierTypeLabel} including{' '}
          <b>{formatNumber(perennialMainstemGainMiles, 2, true)} miles</b> of
          perennial reaches.
        </Box>

        {totalmainstemupstreammiles > 0 ? (
          <Box>
            <b>
              {formatPercent(percentUnaltered)}% of the upstream mainstem
              network
            </b>{' '}
            is in unaltered stream reaches.
          </Box>
        ) : null}

        <Box>
          <b>
            {mainstemsizeclasses} mainstem river size{' '}
            {mainstemsizeclasses === 1 ? 'class' : 'classes'}
          </b>{' '}
          {removed ? 'were' : 'could be'} gained by removing this{' '}
          {barrierTypeLabel}.
        </Box>
      </Grid>

      <Box sx={{ mt: '3rem' }}>
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

          <Row>
            <Box>Ephemeral / intermittent miles</Box>
            <Box>
              {formatNumber(intermittentmainstemupstreammiles, 2, true)}
            </Box>
            <Box>
              {formatNumber(freeintermittentmainstemdownstreammiles, 2, true)}
            </Box>
          </Row>

          <Row>
            <Box>Altered miles</Box>
            <Box>{formatNumber(alteredmainstemupstreammiles, 2, true)}</Box>
            <Box>
              {formatNumber(freealteredmainstemdownstreammiles, 2, true)}
            </Box>
          </Row>

          <Row>
            <Box>Unaltered miles</Box>
            <Box>{formatNumber(unalteredmainstemupstreammiles, 2, true)}</Box>
            <Box>
              {formatNumber(freeunalteredmainstemdownstreammiles, 2, true)}
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
  ...MainstemNetworkPropTypeStub,
  ...LinearDownstreamNetworkPropTypeStub,
  barrierType: PropTypes.string.isRequired,
  networkType: PropTypes.string.isRequired,
  removed: PropTypes.bool,
  sx: PropTypes.object,
}

MainstemNetworkInfo.defaultProps = {
  ...MainstemNetworkDefaultProps,
  ...LinearDownstreamNetworkDefaultProps,
  removed: false,
  sx: null,
}

export default MainstemNetworkInfo
