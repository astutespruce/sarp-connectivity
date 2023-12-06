import React from 'react'
import PropTypes from 'prop-types'
import { Box, Heading, Paragraph, Text } from 'theme-ui'

import { Link } from 'components/Link'
import { Table, Row } from 'components/Table'
import { formatNumber } from 'util/format'

const SpeciesHabitat = ({ habitat, sx }) => {
  const sources = [...new Set(habitat.map(({ source }) => source))]

  return (
    <Box sx={sx}>
      <Heading as="h3">Species habitat information for this network</Heading>

      <Table
        columns="34rem 1fr"
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
        </Row>

        {habitat.map(({ key, label, limit, upstreammiles }) => (
          <Row key={key}>
            <Box>
              <Text>{label}</Text>
              {limit ? (
                <Text variant="help" sx={{ fontSize: 0 }}>
                  Data are known to be limited to {limit} and do not cover the
                  full range of this species.
                </Text>
              ) : null}
            </Box>
            <Box>
              {upstreammiles < 0.1 ? '<0.1' : formatNumber(upstreammiles)}
            </Box>
          </Row>
        ))}
      </Table>

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
  sx: null,
}

export default SpeciesHabitat
