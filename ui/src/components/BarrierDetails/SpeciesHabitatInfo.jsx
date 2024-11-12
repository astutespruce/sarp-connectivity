import React from 'react'
import PropTypes from 'prop-types'
import { Box, Text } from 'theme-ui'

import { barrierTypeLabelSingular } from 'config'
import { Link } from 'components/Link'
import { Entry } from 'components/Sidebar'
import { Table, Row } from 'components/Table'
import { ExpandableParagraph } from 'components/Text'
import { InfoTooltip } from 'components/Tooltip'

import { formatNumber } from 'util/format'

const SpeciesHabitatInfo = ({ barrierType, diadromoushabitat, habitat }) => (
  <>
    <Entry sx={{ pb: '.5rem', mx: '-0.5rem' }}>
      <Table sx={{ fontSize: 1 }} columns="12rem 1fr 1fr">
        <Row sx={{ px: '0.5rem' }}>
          <Box />
          <Box sx={{ fontSize: 0, fontWeight: 'bold' }}>Upstream miles</Box>
          <Box sx={{ fontSize: 0 }}>
            <Text sx={{ fontWeight: 'bold' }}>Downstream miles</Text>
            <Text sx={{ color: 'grey.7' }}>free-flowing miles only</Text>
          </Box>
        </Row>
        {habitat.map(
          ({ key, label, source, limit, upstreammiles, downstreammiles }) => (
            <Row key={key} sx={{ px: '0.5rem' }}>
              <Box>
                <Text sx={{ display: 'inline' }}>{label}</Text>
                <Box sx={{ display: 'inline-block' }}>
                  <InfoTooltip>
                    Estimated instream habitat based on data provided by{' '}
                    {source}.
                    {limit ? (
                      <>
                        <br />
                        Data are known to be limited to {limit}.
                      </>
                    ) : null}
                  </InfoTooltip>
                </Box>
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
    </Entry>

    {diadromoushabitat === 1 ? (
      <Entry>
        This {barrierTypeLabelSingular[barrierType]} is located on a reach with
        anadromous / catadromous species habitat.
      </Entry>
    ) : null}

    <Entry>
      <Text variant="help" sx={{ mt: '1rem', fontSize: 0 }}>
        <ExpandableParagraph
          snippet="Note: instream habitat is estimated from data provided by regional
        partners and assigned to NHDPlusHR flowlines..."
        >
          Note: instream habitat is estimated from data provided by regional
          partners and assigned to NHDPlusHR flowlines; these estimates do not
          fully account for elevation gradients or other natural barriers that
          may have been present in the source data. Habitat data are limited to
          available data sources and are not comprehensive and do not fully
          capture all current or potential habitat for a given species or group
          across its range. For more information, please see the{' '}
          <Link to="/habitat_methods">analysis methods</Link>.
        </ExpandableParagraph>
      </Text>
    </Entry>
  </>
)

SpeciesHabitatInfo.propTypes = {
  barrierType: PropTypes.string.isRequired,
  diadromoushabitat: PropTypes.number,
  habitat: PropTypes.arrayOf(
    PropTypes.shape({
      key: PropTypes.string.isRequired,
      label: PropTypes.string.isRequired,
      source: PropTypes.string.isRequired,
      upstreammiles: PropTypes.number.isRequired,
      downstreammiles: PropTypes.number.isRequired,
      limit: PropTypes.string,
    })
  ).isRequired,
}

SpeciesHabitatInfo.defaultProps = {
  diadromoushabitat: 0,
}

export default SpeciesHabitatInfo
