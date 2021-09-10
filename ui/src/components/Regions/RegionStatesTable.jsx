import React from 'react'
import PropTypes from 'prop-types'
import { Box, Paragraph } from 'theme-ui'

import { Downloader } from 'components/Download'
import { useStateSummary } from 'components/Data'

import { groupBy } from 'util/data'
import { formatNumber } from 'util/format'

import { REGION_STATES, STATES } from '../../../config/constants'

const downloadConfig = { scenario: 'NCWC', layer: 'State' }

const RegionStatesTable = ({
  region,
  dams,
  onNetworkDams,
  smallBarriers,
  onNetworkSmallBarriers,
  totalSmallBarriers,
  ...props
}) => {
  const stateData = groupBy(useStateSummary(), 'id')
  const regionStates = REGION_STATES[region].map((id) => ({ id }))

  const offNetworkDams = dams - onNetworkDams
  const offNetworkBarriers = smallBarriers - onNetworkSmallBarriers

  return (
    <Box {...props}>
      <Box
        sx={{
          mt: '1rem',
          table: {
            width: '100%',
            thead: {
              fontWeight: 'bold',
              fontSize: 1,
              th: {
                bg: 'grey.0',
                borderBottom: '2px solid',
                borderBottomColor: 'grey.3',
                textAlign: 'left',
                py: '0.25em',
              },
              'th:first-of-type': {
                width: '12em',
              },
              'th:nth-of-type(2)': {
                width: '13em',
              },
              'th:nth-of-type(4),th:nth-of-type(5)': {
                width: '12em',
              },
            },
            tbody: {
              td: {
                py: '0.5em',
                borderBottom: '1px solid',
                borderBottomColor: 'grey.1',
              },
              'td:first-of-type': {
                fontWeight: 'bold',
                pl: '0.5em',
              },
              'td:nth-of-type(4),td:nth-of-type(5)': {
                textAlign: 'right',
              },
              'tr:last-of-type td': {
                bg: 'grey.0',
                borderTop: '2px solid',
                borderTopColor: 'grey.3',
              },
            },
            button: {
              fontSize: 1,
              py: '0.25em',
              px: '0.5em',
            },
          },
        }}
      >
        <table cellPadding="0" cellSpacing="0">
          <thead>
            <tr>
              <th />
              <th>Inventoried dams</th>
              <th>Inventoried road-related barriers</th>
              <th />
              <th />
            </tr>
          </thead>
          <tbody>
            {REGION_STATES.se.map((id) => (
              <tr key={id}>
                <td>{STATES[id]}</td>
                <td>{formatNumber(stateData[STATES[id]].dams)} dams </td>
                <td>
                  {formatNumber(stateData[STATES[id]].totalSmallBarriers)}{' '}
                  barriers{' '}
                </td>
                <td>
                  <Downloader
                    label="download dams"
                    asButton
                    barrierType="dams"
                    config={{
                      ...downloadConfig,
                      summaryUnits: [{ id }],
                    }}
                  />
                </td>
                <td>
                  <Downloader
                    label="download barriers"
                    asButton
                    barrierType="small_barriers"
                    config={{
                      ...downloadConfig,
                      summaryUnits: [{ id }],
                    }}
                  />
                </td>
              </tr>
            ))}

            <tr>
              <td>Total</td>
              <td>{formatNumber(dams)} dams</td>
              <td>{formatNumber(totalSmallBarriers)} barriers</td>
              <td>
                <Downloader
                  label="download dams"
                  asButton
                  barrierType="dams"
                  config={{
                    ...downloadConfig,
                    summaryUnits: regionStates,
                  }}
                />
              </td>
              <td>
                <Downloader
                  label="download barriers"
                  asButton
                  barrierType="small_barriers"
                  config={{
                    ...downloadConfig,
                    summaryUnits: regionStates,
                  }}
                />
              </td>
            </tr>
          </tbody>
        </table>
      </Box>

      <Paragraph variant="help" sx={{ mt: '2rem' }}>
        Note: These statistics are based on <i>inventoried</i> dams and
        road-related barriers. Because the inventory is incomplete in many
        areas, areas with a high number of dams may simply represent areas that
        have a more complete inventory.
        <br />
        <br />
        {formatNumber(offNetworkDams, 0)} dams and{' '}
        {formatNumber(offNetworkBarriers, 0)} road-related barriers were not
        analyzed because they could not be correctly located on the aquatic
        network or were otherwise excluded from the analysis.
      </Paragraph>
    </Box>
  )
}

RegionStatesTable.propTypes = {
  region: PropTypes.string.isRequired,
  dams: PropTypes.number,
  onNetworkDams: PropTypes.number,
  smallBarriers: PropTypes.number,
  onNetworkSmallBarriers: PropTypes.number,
  totalSmallBarriers: PropTypes.number,
}

RegionStatesTable.defaultProps = {
  dams: 0,
  onNetworkDams: 0,
  smallBarriers: 0,
  onNetworkSmallBarriers: 0,
  totalSmallBarriers: 0,
}

export default RegionStatesTable
