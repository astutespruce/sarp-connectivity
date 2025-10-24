import React from 'react'
import PropTypes from 'prop-types'
import { Box, Flex, Grid, Paragraph, Spinner, Text } from 'theme-ui'
import { useQuery } from '@tanstack/react-query'
import { ExclamationTriangle } from '@emotion-icons/fa-solid'

import { fetchUnitList } from 'components/Data'
import { Link } from 'components/Link'
import { REGIONS, STATES, ANALYSIS_STATES } from 'config'
import { groupBy } from 'util/data'
import { formatNumber } from 'util/format'

import Downloader from './Downloader'

const downloadConfig = { scenario: 'NCWC', layer: 'State' }

const StateDownloadTable = ({
  region,
  dams,
  rankedDams,
  reconDams,
  smallBarriers,
  rankedSmallBarriers,
  totalSmallBarriers,
  sx,
}) => {
  let states = []
  if (region === 'total') {
    states = ANALYSIS_STATES
  } else {
    states = REGIONS[region].states
  }

  const unrankedDams = dams - rankedDams
  const unrankedBarriers = smallBarriers - rankedSmallBarriers

  const { isLoading, error, data } = useQuery({
    queryKey: ['StatesList', states],
    queryFn: async () => fetchUnitList('State', states),

    staleTime: 60 * 60 * 1000, // 60 minutes
    // staleTime: 1, // use then reload to force refresh of underlying data during dev
    refetchOnWindowFocus: false,
    refetchOnMount: false,
  })

  if (isLoading) {
    return (
      <Flex sx={{ justifyContent: 'center' }}>
        <Spinner />
      </Flex>
    )
  }

  if (error) {
    console.error(`Error loading state table for states: ${states.join(',')}`)
    return (
      <Flex
        sx={{
          justifyContent: 'center',
          alignItems: 'center',
          gap: '1rem',
          color: 'highlight',
        }}
      >
        <Box>
          <ExclamationTriangle size="2em" />
        </Box>
        <Text>
          Whoops! There was an error loading the states in this region
        </Text>
      </Flex>
    )
  }

  const stateData = groupBy(data, 'id')

  return (
    <Box sx={sx}>
      <Box
        sx={{
          mt: '1rem',
          table: {
            width: '100%',
            thead: {
              fontWeight: 'bold',
              fontSize: 1,
              th: {
                bg: 'blue.1',
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
              <th aria-label="state column"> </th>
              <th>Inventoried dams</th>
              <th>Reconned dams</th>
              <th>Assessed road-related barriers</th>
              <th aria-label="dams download link column"> </th>
              <th aria-label="road barriers download link column"> </th>
            </tr>
          </thead>
          <tbody>
            {states
              .sort((a, b) => (STATES[a] < STATES[b] ? -1 : 1))
              .map((id) => (
                <tr key={id}>
                  <td>
                    <Link to={`/states/${id}`}>{STATES[id]}</Link>
                  </td>
                  <td>{formatNumber(stateData[id].dams)}</td>
                  <td>{formatNumber(stateData[id].reconDams)}</td>
                  <td>{formatNumber(stateData[id].totalSmallBarriers)}</td>
                  <td>
                    <Downloader
                      label="dams"
                      barrierType="dams"
                      disabled={stateData[id].dams === 0}
                      showOptions={false}
                      includeUnranked
                      config={{
                        ...downloadConfig,
                        summaryUnits: { State: [id] },
                      }}
                    />
                  </td>
                  <td>
                    <Downloader
                      label="barriers"
                      barrierType="small_barriers"
                      disabled={stateData[id].totalSmallBarriers === 0}
                      showOptions={false}
                      includeUnranked
                      config={{
                        ...downloadConfig,
                        summaryUnits: { State: [id] },
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
                  barrierType="dams"
                  disabled={dams === 0}
                  config={{
                    ...downloadConfig,
                    summaryUnits: { State: states.map((id) => id) },
                  }}
                />
              </td>
              <td>
                <Downloader
                  label="barriers"
                  barrierType="small_barriers"
                  disabled={totalSmallBarriers === 0}
                  config={{
                    ...downloadConfig,
                    summaryUnits: { State: states.map((id) => id) },
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
            {formatNumber(unrankedBarriers, 0)} assessed road-related barriers
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
  sx: PropTypes.object,
}

StateDownloadTable.defaultProps = {
  dams: 0,
  rankedDams: 0,
  reconDams: 0,
  smallBarriers: 0,
  rankedSmallBarriers: 0,
  totalSmallBarriers: 0,
  sx: {},
}

export default StateDownloadTable
