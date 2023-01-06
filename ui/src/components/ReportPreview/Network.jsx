import React from 'react'
import PropTypes from 'prop-types'
import { Box, Grid, Heading, Paragraph, Text } from 'theme-ui'

import { Table, Row } from 'components/Table'
import { siteMetadata, barrierTypeLabelSingular } from 'config'
import { formatNumber, formatPercent } from 'util/format'

const { version: dataVersion } = siteMetadata

const Network = ({
  barrierType,
  sarpid,
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
  excluded,
  diversion,
  nostructure,
  hasnetwork,
  onloop,
  invasive,
  unranked,
  sx,
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

  const header = <Heading as="h3">Functional network information</Heading>

  if (excluded) {
    if (diversion && nostructure) {
      return (
        <Box sx={sx}>
          {header}
          <Text>
            This water diversion was excluded from the connectivity analysis
            because it does not have an associated in-stream barrier.
          </Text>
        </Box>
      )
    }

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

      <Grid
        columns={totalupstreammiles > 0 ? 4 : 3}
        gap={0}
        sx={{
          mt: '2rem',
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
          <b>{formatNumber(gainmiles, 2, true)} total miles</b> could be
          reconnected by removing this {barrierTypeLabel} including{' '}
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
          could be gained by removing this {barrierTypeLabel}.
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
        </Table>
      </Box>

      {invasive ? (
        <Paragraph variant="help" sx={{ mt: '2rem', fontSize: 0 }}>
          Note: this {barrierTypeLabel} is identified as a beneficial to
          restricting the movement of invasive species and is not ranked.
        </Paragraph>
      ) : null}

      {unranked && !invasive ? (
        <Paragraph variant="help" sx={{ mt: '2rem', fontSize: 0 }}>
          Note: this {barrierTypeLabel} excluded from ranking based on field
          reconnaissance, manual review of aerial imagery, or other information
          about this {barrierTypeLabel}.
        </Paragraph>
      ) : null}

      <Paragraph variant="help" sx={{ mt: '2rem', fontSize: 0 }}>
        Note: downstream lengths are limited to free-flowing reaches only; these
        exclude lengths within waterbodies in the downstream network. Perennial
        miles are the sum of lengths of all reaches not specifically coded as
        ephemeral or intermittent within the functional network. Perennial
        reaches are not necessarily contiguous. Altered miles are the total
        length of stream reaches that are specifically identified in NHD or the
        National Wetlands Inventory as altered (canal / ditch, within a
        reservoir, or other channel alteration), and do not necessarily include
        all forms of alteration of the stream channel.
      </Paragraph>
    </Box>
  )
}

Network.propTypes = {
  barrierType: PropTypes.string.isRequired,
  sarpid: PropTypes.string.isRequired,
  hasnetwork: PropTypes.bool.isRequired,
  excluded: PropTypes.bool,
  onloop: PropTypes.bool,
  diversion: PropTypes.number,
  nostructure: PropTypes.bool,
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
  sx: PropTypes.object,
}

Network.defaultProps = {
  excluded: false,
  onloop: false,
  diversion: 0,
  nostructure: false,
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
  sx: null,
}

export default Network
