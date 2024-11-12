import React from 'react'
import PropTypes from 'prop-types'
import { Box, Heading, Paragraph, Text } from 'theme-ui'

import { barrierTypeLabelSingular } from 'config'
import { Link } from 'components/Link'
import { Table, Row } from 'components/Table'
import { formatNumber } from 'util/format'

const SpeciesHabitat = ({ barrierType, diadromoushabitat, habitat, sx }) => {
  const sources = [...new Set(habitat.map(({ source }) => source))]

  return (
    <Box sx={sx}>
      <Heading as="h3">Species habitat information for this network</Heading>

      <Table
        columns="1fr 10rem 10rem"
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
            <b>upstream miles</b>
          </Box>
          <Box>
            <b>downstream miles</b>
            <br />
            <Text sx={{ color: 'grey.7', fontSize: 0 }}>
              free-flowing miles only
            </Text>
          </Box>
        </Row>

        {habitat.map(
          ({ key, label, limit, upstreammiles, downstreammiles }) => (
            <Row key={key}>
              <Box>
                <Text>{label}</Text>
                {limit ? (
                  <Text variant="help" sx={{ fontSize: 0 }}>
                    Data are known to be limited to {limit}.
                  </Text>
                ) : null}
              </Box>
              <Box>
                {upstreammiles > 0 && upstreammiles < 0.1
                  ? '<0.1'
                  : formatNumber(upstreammiles)}
              </Box>
              <Box>
                {downstreammiles > 0 && downstreammiles < 0.1
                  ? '<0.1'
                  : formatNumber(downstreammiles)}
              </Box>
            </Row>
          )
        )}
      </Table>

      {diadromoushabitat === 1 ? (
        <Box sx={{ mt: '2rem' }}>
          This {barrierTypeLabelSingular[barrierType]} is located on a reach
          with anadromous / catadromous species habitat.
        </Box>
      ) : null}

      <Paragraph variant="help" sx={{ mt: '2rem', fontSize: 0 }}>
        Note: instream habitat is estimated from data provided by regional
        partners ({sources.join(', ')}) and assigned to NHDPlusHR flowlines;
        these estimates do not fully account for elevation gradients or other
        natural barriers that may have been present in the source data. Habitat
        data are limited to available data sources and are not comprehensive and
        do not fully capture all current or potential habitat for a given
        species or group across its range. For more information, please see the{' '}
        <Link to="/habitat_methods">analysis methods</Link>.
      </Paragraph>
    </Box>
  )
}

SpeciesHabitat.propTypes = {
  barrierType: PropTypes.string.isRequired,
  diadromoushabitat: PropTypes.number,
  habitat: PropTypes.arrayOf(
    PropTypes.shape({
      key: PropTypes.string.isRequired,
      label: PropTypes.string.isRequired,
      source: PropTypes.string.isRequired,
      upstreammiles: PropTypes.number.isRequired,
      limit: PropTypes.string,
    })
  ).isRequired,
  sx: PropTypes.object,
}

SpeciesHabitat.defaultProps = {
  diadromoushabitat: 0,
  sx: null,
}

export default SpeciesHabitat
