import React from 'react'
import PropTypes from 'prop-types'
import { Box, Grid, Heading, Paragraph, Text } from 'theme-ui'

import { Table, Row } from 'components/Table'
import { formatNumber, formatPercent } from 'util/format'

import { siteMetadata } from '../../../gatsby-config'

const { version: dataVersion } = siteMetadata

const Network = ({
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
  excluded,
  hasnetwork,
  sarpid,
  ...props
}) => {
  const barrierTypeLabel =
    barrierType === 'dams' ? 'dam' : 'road-related barrier'
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
    return (
      <Box {...props}>
        {header}
        <Text>
          This dam was excluded from the connectivity analysis based on field
          reconnaissance or manual review of aerial imagery.
        </Text>
      </Box>
    )
  }

  if (!hasnetwork) {
    return (
      <Box {...props}>
        {header}
        <Text sx={{ mt: '0.5rem' }}>
          This dam is off-network and has no functional network information.
        </Text>

        <Paragraph variant="help" sx={{ mt: '0.5rem', fontSize: 0 }}>
          Not all dams could be correctly snapped to the aquatic network for
          analysis. Please{' '}
          <a
            href={`mailto:Kat@southeastaquatics.net?subject=Problem with SARP Inventory for ${
              barrierType === 'dams' ? 'dam' : 'road-related barrier'
            }: ${sarpid} (data version: ${dataVersion})&body=I found the following problem with the SARP Inventory for this barrier:`}
          >
            contact us
          </a>{' '}
          to report an error or for assistance interpreting these results.
        </Paragraph>
      </Box>
    )
  }

  return (
    <Box {...props}>
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
          reconnected by removing this {barrierTypeLabel}, including{' '}
          <b>{formatNumber(perennialGainMiles, 2, true)} miles</b> of perennial
          reaches.
        </Box>

        {totalupstreammiles > 0 ? (
          <Box>
            <b>{formatPercent(percentAltered)}% of the upstream network</b> is
            in altered stream channels (coded as canals / ditches).
          </Box>
        ) : null}

        <Box>
          <b>
            {sizeclasses} river size {sizeclasses === 1 ? 'class' : 'classes'}
          </b>{' '}
          could be gained by removing this barrier.
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
      <Paragraph variant="help" sx={{ mt: '2rem', fontSize: 0 }}>
        Note: downstream lengths are limited to free-flowing reaches only; these
        exclude lengths within waterbodies in the downstream network. Perennial
        miles are the sum of lengths of all reaches not specifically coded as
        ephemeral or intermittent within the functional network. Perennial
        reaches are not necessarily contiguous. Altered miles are those that are
        specifically coded as canals or ditches, and do not necessarily include
        all forms of alteration of the stream channel.
      </Paragraph>
    </Box>
  )
}

Network.propTypes = {
  barrierType: PropTypes.string.isRequired,
  hasnetwork: PropTypes.bool.isRequired,
  excluded: PropTypes.bool,
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
  sarpid: PropTypes.string.isRequired,
}

Network.defaultProps = {
  excluded: false,
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

export default Network
