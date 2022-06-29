import React from 'react'
import PropTypes from 'prop-types'
import { Box, Grid, Paragraph } from 'theme-ui'

import { useStateSummary } from 'components/Data'

import { groupBy } from 'util/data'
import { formatNumber } from 'util/format'

import Downloader from './Downloader'
import { REGION_STATES, STATES } from '../../../config/constants'

const downloadConfig = { scenario: 'NCWC', layer: 'State' }

const StateDownloadTable = ({
  region,
  dams,
  rankedDams,
  reconDams,
  smallBarriers,
  rankedSmallBarriers,
  totalSmallBarriers,
  ...props
}) => {
  const stateData = groupBy(useStateSummary(), 'id')
  const regionStates = REGION_STATES[region]

  const unrankedDams = dams - rankedDams
  const unrankedBarriers = smallBarriers - rankedSmallBarriers

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
                py: '1rem',
              },
              'th + th': {
                ml: '0.5rem',
              },
              'th:first-of-type': {
                width: '16em',
              },
              'th:nth-of-type(2),th:nth-of-type(3),th:nth-of-type(4)': {
                width: '12em',
                flex: '0 0 auto',
              },
              'th:nth-of-type(5),th:nth-of-type(6)': {
                width: '8em',
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
              'td:nth-of-type(5),td:nth-of-type(6)': {
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
        <table cellPadding="0.5rem" cellSpacing="0">
          <thead>
            <tr>
              <th> </th>
              <th>Inventoried dams</th>
              <th>Reconned dams</th>
              <th>Inventoried road-related barriers</th>
              <th> </th>
              <th> </th>
            </tr>
          </thead>
          <tbody>
            {regionStates.map((id) => (
              <tr key={id}>
                <td>{STATES[id]}</td>
                <td>{formatNumber(stateData[id].dams)}</td>
                <td>{formatNumber(stateData[id].reconDams)}</td>
                <td>{formatNumber(stateData[id].totalSmallBarriers)}</td>
                <td>
                  <Downloader
                    label="dams"
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
                    label="barriers"
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
              <td>{formatNumber(dams)}</td>
              <td>{formatNumber(reconDams)}</td>
              <td>{formatNumber(totalSmallBarriers)}</td>
              <td>
                <Downloader
                  label="dams"
                  asButton
                  barrierType="dams"
                  config={{
                    ...downloadConfig,
                    summaryUnits: regionStates.map((id) => ({ id })),
                  }}
                />
              </td>
              <td>
                <Downloader
                  label="barriers"
                  asButton
                  barrierType="small_barriers"
                  config={{
                    ...downloadConfig,
                    summaryUnits: regionStates.map((id) => ({ id })),
                  }}
                />
              </td>
            </tr>
          </tbody>
        </table>
      </Box>

      <Grid columns={[0, 2]} gap={4} sx={{ mt: '2rem' }}>
        <Paragraph variant="help">
          <b>{formatNumber(unrankedDams, 0)} inventoried dams</b> and{' '}
          <b>
            {formatNumber(unrankedBarriers, 0)} inventoried road-related
            barriers
          </b>{' '}
          were not analyzed because they could not be correctly located on the
          aquatic network or were otherwise excluded from the analysis. You can
          optionally include these in your download.
        </Paragraph>
        <Paragraph variant="help">
          Note: These statistics are based on <i>inventoried</i> dams and
          road-related barriers. Because the inventory is incomplete in many
          areas, areas with a high number of dams may simply represent areas
          that have a more complete inventory.
        </Paragraph>
      </Grid>
    </Box>
  )
}

StateDownloadTable.propTypes = {
  region: PropTypes.string.isRequired,
  dams: PropTypes.number,
  rankedDams: PropTypes.number,
  reconDams: PropTypes.number,
  smallBarriers: PropTypes.number,
  rankedSmallBarriers: PropTypes.number,
  totalSmallBarriers: PropTypes.number,
}

StateDownloadTable.defaultProps = {
  dams: 0,
  rankedDams: 0,
  reconDams: 0,
  smallBarriers: 0,
  rankedSmallBarriers: 0,
  totalSmallBarriers: 0,
}

export default StateDownloadTable
