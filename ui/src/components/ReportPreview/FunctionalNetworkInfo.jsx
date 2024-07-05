import React from 'react'
import PropTypes from 'prop-types'
import { Box, Grid, Heading, Paragraph, Text } from 'theme-ui'

import { OutboundLink } from 'components/Link'
import { Table, Row } from 'components/Table'
import { siteMetadata, barrierTypeLabelSingular } from 'config'
import { formatNumber, formatPercent } from 'util/format'

const { version: dataVersion } = siteMetadata

const FunctionalNetworkInfo = ({
  barrierType,
  networkType,
  sarpid,
  totalupstreammiles,
  perennialupstreammiles,
  alteredupstreammiles,
  unalteredupstreammiles,
  resilientupstreammiles,
  freedownstreammiles,
  freeperennialdownstreammiles,
  freealtereddownstreammiles,
  freeunaltereddownstreammiles,
  freeresilientdownstreammiles,
  sizeclasses,
  landcover,
  excluded,
  hasnetwork,
  in_network_type,
  onloop,
  invasive,
  unranked,
  removed,
  yearremoved,
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

  const percentAltered = totalupstreammiles
    ? (100 * alteredupstreammiles) / totalupstreammiles
    : 0

  const header = <Heading as="h3">Functional network information</Heading>

  if (excluded) {
    return (
      <Box sx={sx}>
        {header}
        <Text>
          This {barrierTypeLabel} was excluded from the connectivity analysis
          based on field reconnaissance or manual review of aerial imagery.
        </Text>
      </Box>
    )
  }

  if (onloop) {
    return (
      <Box sx={sx}>
        {header}
        <Text sx={{ mt: '0.5rem' }}>
          This {barrierTypeLabel} was excluded from the connectivity analysis
          based on its position within the aquatic network.
        </Text>

        <Paragraph variant="help" sx={{ mt: '0.5rem', fontSize: 0 }}>
          This {barrierTypeLabel} was snapped to a secondary channel within the
          aquatic network according to the way that primary versus secondary
          channels are identified within the NHD High Resolution Plus dataset.
          This {barrierTypeLabel} may need to be repositioned to occur on the
          primary channel in order to be included within the connectivity
          analysis. Please{' '}
          <a
            href={`mailto:Kat@southeastaquatics.net?subject=Problem with SARP Inventory for ${barrierTypeLabel}: ${sarpid} (data version: ${dataVersion})&body=I found the following problem with the SARP Inventory for this barrier:`}
          >
            contact us
          </a>{' '}
          to report an error.
        </Paragraph>
      </Box>
    )
  }

  if (!in_network_type) {
    return (
      <Box sx={sx}>
        {header}
        <Text sx={{ mt: '0.5rem' }}>
          This {barrierTypeLabel} is not included in this network scenario based
          on its passability
          {networkType === 'largefish_barriers'
            ? ' for large-bodied fish '
            : null}
          {networkType === 'smallfish_barriers'
            ? ' for small-bodied fish '
            : null}
          and has no functional network information.
        </Text>
      </Box>
    )
  }

  if (!hasnetwork) {
    return (
      <Box sx={sx}>
        {header}
        <Text sx={{ mt: '0.5rem' }}>
          This {barrierTypeLabel} is off-network and has no functional network
          information.
        </Text>

        <Paragraph variant="help" sx={{ mt: '0.5rem', fontSize: 0 }}>
          Not all dams could be correctly snapped to the aquatic network for
          analysis. Please{' '}
          <a
            href={`mailto:Kat@southeastaquatics.net?subject=Problem with SARP Inventory for ${barrierTypeLabel}: ${sarpid} (data version: ${dataVersion})&body=I found the following problem with the SARP Inventory for this barrier:`}
          >
            contact us
          </a>{' '}
          to report an error or for assistance interpreting these results.
        </Paragraph>
      </Box>
    )
  }

  return (
    <Box sx={sx}>
      {header}

      <Paragraph variant="help" sx={{ fontSize: 0 }}>
        Functional networks are the full upstream dendritic network to the
        upstream-most points on the network or upstream barriers. The downstream
        network is the upstream functional network of the next barrier
        immediately downstream or downstream-most point on that network, and
        includes any tributaries up to their upstream-most points or other
        barriers.
      </Paragraph>

      {removed ? (
        <Text>
          {yearremoved !== null && yearremoved > 0
            ? `This barrier was removed or mitigated in ${yearremoved}.`
            : 'This barrier has been removed or mitigated.'}
        </Text>
      ) : null}

      <Grid
        columns={totalupstreammiles > 0 ? 4 : 3}
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
          <b>{formatNumber(gainmiles, 2, true)} total miles</b>{' '}
          {removed ? 'were' : 'could be'} reconnected by removing this{' '}
          {barrierTypeLabel} including{' '}
          <b>{formatNumber(perennialGainMiles, 2, true)} miles</b> of perennial
          reaches.
        </Box>

        {totalupstreammiles > 0 ? (
          <Box>
            <b>{formatPercent(percentAltered)}% of the upstream network</b> is
            in altered stream reaches.
          </Box>
        ) : null}

        <Box>
          <b>
            {sizeclasses} river size {sizeclasses === 1 ? 'class' : 'classes'}
          </b>{' '}
          {removed ? 'were' : 'could be'} gained by removing this{' '}
          {barrierTypeLabel}.
        </Box>

        <Box>
          <b>{formatNumber(landcover, 0)}% of the upstream floodplain</b> is
          composed of natural landcover.
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
            <Box sx={{ fontStyle: 'italic' }}>Network statistics:</Box>
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
            <Box>Perennial miles</Box>
            <Box
              sx={{
                fontWeight:
                  perennialGainMilesSide === 'upstream' ? 'bold' : 'inherited',
              }}
            >
              {formatNumber(perennialupstreammiles, 2, true)}
            </Box>
            <Box
              sx={{
                fontWeight:
                  perennialGainMilesSide === 'downstream'
                    ? 'bold'
                    : 'inherited',
              }}
            >
              {formatNumber(freeperennialdownstreammiles, 2, true)}
            </Box>
          </Row>

          <Row>
            <Box>Ephemeral / intermittent miles</Box>
            <Box>{formatNumber(intermittentupstreammiles, 2, true)}</Box>
            <Box>{formatNumber(freeintermittentdownstreammiles, 2, true)}</Box>
          </Row>

          <Row>
            <Box>Altered miles</Box>
            <Box>{formatNumber(alteredupstreammiles, 2, true)}</Box>
            <Box>{formatNumber(freealtereddownstreammiles, 2, true)}</Box>
          </Row>

          <Row>
            <Box>Unaltered miles</Box>
            <Box>{formatNumber(unalteredupstreammiles, 2, true)}</Box>
            <Box>{formatNumber(freeunaltereddownstreammiles, 2, true)}</Box>
          </Row>

          <Row>
            <Box>Resilient miles</Box>
            <Box>{formatNumber(resilientupstreammiles, 2, true)}</Box>
            <Box>{formatNumber(freeresilientdownstreammiles, 2, true)}</Box>
          </Row>
        </Table>
      </Box>

      {unranked && !invasive ? (
        <Paragraph variant="help" sx={{ mt: '2rem', fontSize: 0 }}>
          Note: this {barrierTypeLabel} excluded from ranking based on field
          reconnaissance, manual review of aerial imagery, or other information
          about this {barrierTypeLabel}.
        </Paragraph>
      ) : null}

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
        . Downstream lengths are limited to free-flowing reaches only; these
        exclude lengths within waterbodies in the downstream network. Perennial
        miles are the sum of lengths of all reaches not specifically coded as
        ephemeral or intermittent within the functional network. Perennial
        reaches are not necessarily contiguous. Altered miles are the total
        length of stream reaches that are specifically identified in NHD or the
        National Wetlands Inventory as altered (canal / ditch, within a
        reservoir, or other channel alteration), and do not necessarily include
        all forms of alteration of the stream channel. Resilient miles are the
        total length of stream reaches that are within watersheds with above
        average or greater freshwater resilience within{' '}
        <OutboundLink to="https://www.maps.tnc.org/resilientrivers/#/explore">
          The Nature Conservancy&apos;s Freshwater Resilience
        </OutboundLink>{' '}
        dataset (v0.44).
      </Paragraph>
    </Box>
  )
}

FunctionalNetworkInfo.propTypes = {
  barrierType: PropTypes.string.isRequired,
  networkType: PropTypes.string.isRequired,
  sarpid: PropTypes.string.isRequired,
  hasnetwork: PropTypes.bool.isRequired,
  in_network_type: PropTypes.bool.isRequired,
  excluded: PropTypes.bool,
  onloop: PropTypes.bool,
  totalupstreammiles: PropTypes.number,
  perennialupstreammiles: PropTypes.number,
  alteredupstreammiles: PropTypes.number,
  unalteredupstreammiles: PropTypes.number,
  resilientupstreammiles: PropTypes.number,
  freedownstreammiles: PropTypes.number,
  freeperennialdownstreammiles: PropTypes.number,
  freealtereddownstreammiles: PropTypes.number,
  freeunaltereddownstreammiles: PropTypes.number,
  freeresilientdownstreammiles: PropTypes.number,
  landcover: PropTypes.number,
  sizeclasses: PropTypes.number,
  invasive: PropTypes.bool,
  unranked: PropTypes.bool,
  removed: PropTypes.bool,
  yearremoved: PropTypes.number,
  flowstoocean: PropTypes.number,
  flowstogreatlakes: PropTypes.number,
  totaldownstreamdams: PropTypes.number,
  totaldownstreamsmallbarriers: PropTypes.number,
  totaldownstreamwaterfalls: PropTypes.number,
  sx: PropTypes.object,
}

FunctionalNetworkInfo.defaultProps = {
  excluded: false,
  onloop: false,
  totalupstreammiles: 0,
  perennialupstreammiles: 0,
  alteredupstreammiles: 0,
  unalteredupstreammiles: 0,
  resilientupstreammiles: 0,
  freedownstreammiles: 0,
  freeperennialdownstreammiles: 0,
  freealtereddownstreammiles: 0,
  freeunaltereddownstreammiles: 0,
  freeresilientdownstreammiles: 0,
  landcover: 0,
  sizeclasses: 0,
  invasive: false,
  unranked: false,
  removed: false,
  yearremoved: 0,
  flowstoocean: 0,
  flowstogreatlakes: 0,
  totaldownstreamdams: 0,
  totaldownstreamsmallbarriers: 0,
  totaldownstreamwaterfalls: 0,
  sx: null,
}

export default FunctionalNetworkInfo
