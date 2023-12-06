import React from 'react'
import PropTypes from 'prop-types'
import { Box, Text } from 'theme-ui'

import { Link } from 'components/Link'
import { Entry } from 'components/Sidebar'
import { Table, Row } from 'components/Table'
import { InfoTooltip } from 'components/Tooltip'

import { formatNumber } from 'util/format'

const SpeciesHabitatInfo = ({ habitat }) => (
  <>
    <Entry sx={{ pb: '.5rem', mx: '-0.5rem' }}>
      <Table sx={{ fontSize: 1 }} columns="18rem 1fr">
        <Row sx={{ px: '0.5rem' }}>
          <Box />
          <Box sx={{ fontSize: 0 }}>
            <b>Upstream miles</b>
          </Box>
        </Row>
        {habitat.map(({ key, label, source, limit, upstreammiles }) => (
          <Row key={key} sx={{ px: '0.5rem' }}>
            <Box>
              <Text sx={{ display: 'inline' }}>{label}</Text>
              <Box sx={{ display: 'inline-block' }}>
                <InfoTooltip>
                  Estimated instream habitat based on data provided by {source}.
                  {limit ? (
                    <>
                      <br />
                      Data are known to be limited to {limit} and do not cover
                      the full range of this species.
                    </>
                  ) : null}
                </InfoTooltip>
              </Box>
            </Box>
            <Box>
              {upstreammiles < 0.1 ? '<0.1' : formatNumber(upstreammiles)}
            </Box>
          </Row>
        ))}
      </Table>
    </Entry>
    <Entry>
      <Text variant="help" sx={{ mt: '1rem', fontSize: 0 }}>
        Note: instream habitat is estimated from data provided by regional
        partners and assigned to NHDPlusHR flowlines; these estimates do not
        fully account for elevation gradients or other natural barriers that may
        have been present in the source data. Habitat data are limited to
        available data sources and are not comprehensive and do not fully
        capture all current or potential habitat for a given species or group
        across its range. For more information, please see the{' '}
        <Link to="/habitat_methods">analysis methods</Link>.
      </Text>
    </Entry>
  </>
)

SpeciesHabitatInfo.propTypes = {
  habitat: PropTypes.arrayOf(
    PropTypes.shape({
      key: PropTypes.string.isRequired,
      label: PropTypes.string.isRequired,
      source: PropTypes.string.isRequired,
      upstreammiles: PropTypes.number.isRequired,
      limit: PropTypes.string,
    })
  ).isRequired,
}

export default SpeciesHabitatInfo
