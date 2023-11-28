/* eslint-disable camelcase */
import React from 'react'
import PropTypes from 'prop-types'
import { Box, Button, Heading, Flex, Text, Paragraph } from 'theme-ui'

import { ExternalLink } from 'components/Link'
import { STATE_FIPS, STATES, CONNECTIVITY_TEAMS } from 'config'
import { formatNumber, pluralize } from 'util/format'

import Chart from './Chart'
import { layers } from './layers'
import { extractYearRemovedStats } from './util'

const UnitDetails = ({
  barrierType,
  summaryUnit,
  metric,
  onChangeMetric,
  onClose,
}) => {
  const teams = {}
  Object.values(CONNECTIVITY_TEAMS).forEach((region) => {
    Object.entries(region).forEach(([state, info]) => {
      teams[state] = info
    })
  })

  const {
    id,
    layerId,
    dams = 0,
    removedDams = 0,
    removedDamsGainMiles = 0,
    removedDamsByYear = '',
    totalSmallBarriers = 0,
    removedSmallBarriers = 0,
    removedSmallBarriersGainMiles = 0,
    removedSmallBarriersByYear = '',
  } = summaryUnit

  let { name = '' } = summaryUnit

  const layerConfig = layers.filter(({ id: lyrID }) => lyrID === layerId)[0]
  let { title: layerTitle } = layerConfig

  let title = null
  let state = null
  let team = null
  if (layerId === 'County') {
    title = `${name} County`
    state = STATE_FIPS[id.slice(0, 2)]
    layerTitle = state
  }

  if (layerId === 'State') {
    state = STATES[id]
    name = state
    team = teams[id]
  }

  title = name || id

  const removedBarriersByYear = extractYearRemovedStats(
    removedDamsByYear,
    removedSmallBarriersByYear
  )
  console.log('removed', removedBarriersByYear)

  return (
    <Flex sx={{ flexDirection: 'column', height: '100%' }}>
      <Flex
        sx={{
          py: '1rem',
          pl: '1rem',
          pr: '0.5rem',
          justifyContent: 'center',
          alignItems: 'flex-start',
          borderBottom: '1px solid #DDD',
          bg: '#f6f6f2',
          lineHeight: 1.2,
        }}
      >
        <Box sx={{ flex: '1 1 auto' }}>
          <Heading as="h3" sx={{ m: 0, fontSize: '1.25rem' }}>
            {title}
          </Heading>
          {layerId !== 'State' && layerId !== 'HUC2' ? (
            <Text sx={{ fontSize: '1.25rem' }}>{layerTitle}</Text>
          ) : null}
          {layerId === 'HUC6' ||
          layerId === 'HUC8' ||
          layerId === 'HUC10' ||
          layerId === 'HUC12' ? (
            <Text sx={{ color: 'grey.7' }}>
              {layerId}: {id}
            </Text>
          ) : null}
        </Box>

        <Button variant="close" onClick={onClose}>
          &#10006;
        </Button>
      </Flex>
      <Box
        sx={{
          p: '1rem',
          flex: '1 1 auto',
          height: '100%',
          overflowY: 'auto',
        }}
      >
        <Paragraph>This area contains:</Paragraph>

        {barrierType === 'dams' || barrierType === 'combined_barriers' ? (
          <Paragraph sx={{ mt: '0.5rem' }}>
            {removedDams > 0 ? (
              <>
                <b>
                  {formatNumber(removedDams, 0)} {pluralize('dam', removedDams)}
                </b>{' '}
                that {removedDams === 1 ? 'has' : 'have'} been removed or
                mitigated, gaining{' '}
                <b>{formatNumber(removedDamsGainMiles)} miles</b> of reconnected
                rivers and streams
              </>
            ) : (
              <>
                <b>0</b> dams that are known to have been removed or mitigated
              </>
            )}
          </Paragraph>
        ) : null}

        {barrierType === 'small_barriers' ||
        barrierType === 'combined_barriers' ? (
          <Paragraph
            sx={{
              mt: barrierType === 'combined_barriers' ? '1.5rem' : '0.5rem',
            }}
          >
            {removedSmallBarriers ? (
              <>
                <b>{formatNumber(removedSmallBarriers, 0)}</b>{' '}
                {pluralize('road-related barrier', removedSmallBarriers)} that{' '}
                {removedSmallBarriers === 1 ? 'has' : 'have'} been removed or
                mitigated, gaining{' '}
                <b>{formatNumber(removedSmallBarriersGainMiles)} miles</b> of
                reconnected rivers and streams
              </>
            ) : (
              <>
                <b>0</b> road-related barriers that are known to have been
                removed or mitigated
              </>
            )}
          </Paragraph>
        ) : null}

        <Box sx={{ mt: '2rem' }}>
          <Chart
            barrierType={barrierType}
            removedBarriersByYear={removedBarriersByYear}
            metric={metric}
            onChangeMetric={onChangeMetric}
          />
        </Box>

        {barrierType === 'dams' ? (
          <Paragraph variant="help" sx={{ mt: '2rem' }}>
            Note: These statistics are based on <b>{formatNumber(dams, 0)}</b>{' '}
            inventoried {pluralize('dam', dams)} and available information on
            dams that have been removed or mitigated. Because the inventory is
            incomplete in many areas, areas with a high number of dams may
            simply represent areas that have a more complete inventory.
          </Paragraph>
        ) : null}

        {barrierType === 'small_barriers' ? (
          <Paragraph variant="help" sx={{ mt: '2rem' }}>
            Note: These statistics are based on{' '}
            {formatNumber(totalSmallBarriers, 0)} inventoried road-related
            barriers that have been assessed for impacts to aquatic organisms
            and available information on barriers that have been removed or
            mitigated. Because the inventory is incomplete in many areas, areas
            with a high number of barriers may simply represent areas that have
            a more complete inventory.
          </Paragraph>
        ) : null}

        {barrierType === 'combined_barriers' ? (
          <Paragraph variant="help" sx={{ mt: '2rem' }}>
            Note: These statistics are based on {formatNumber(dams, 0)}{' '}
            inventoried {pluralize('dam', dams)} and{' '}
            {formatNumber(totalSmallBarriers, 0)} inventoried{' '}
            {pluralize('road-related barrier', totalSmallBarriers)} that have
            been assessed for impacts to aquatic organisms, and available
            information on barriers that have been removed or mitigated. Because
            the inventory is incomplete in many areas, areas with a high number
            of barriers may simply represent areas that have a more complete
            inventory.
          </Paragraph>
        ) : null}

        <Paragraph variant="help" sx={{ mt: '1rem' }}>
          Miles gained are based on aquatic networks cut by{' '}
          {barrierType === 'dams'
            ? 'waterfalls and dams'
            : 'waterfalls, dams, and road-related barriers'}{' '}
          that were present at the time a given barrier was removed, with the
          exception of those directly upstream that were removed in the same
          year as a given barrier.
        </Paragraph>

        {team ? (
          <Box
            sx={{
              mt: '3rem',
              borderTop: '1px solid',
              borderTopColor: 'grey.1',
              pt: '1rem',
            }}
          >
            <Text>
              This state has an active Aquatic Connectivity Team: the{' '}
              {team.name}.{' '}
              <Text sx={{ display: 'inline-block' }}>
                <ExternalLink to={team.url}>
                  Learn more about this team
                </ExternalLink>
              </Text>
            </Text>
          </Box>
        ) : null}
      </Box>
    </Flex>
  )
}

UnitDetails.propTypes = {
  barrierType: PropTypes.string.isRequired,
  summaryUnit: PropTypes.shape({
    id: PropTypes.oneOfType([PropTypes.string, PropTypes.number]).isRequired,
    layerId: PropTypes.string.isRequired,
    name: PropTypes.string,
    dams: PropTypes.number,
    rankedDams: PropTypes.number,
    removedDams: PropTypes.number,
    removedDamsGainMiles: PropTypes.number,
    removedDamsByYear: PropTypes.string,
    smallBarriers: PropTypes.number,
    totalSmallBarriers: PropTypes.number,
    rankedSmallBarriers: PropTypes.number,
    removedSmallBarriers: PropTypes.number,
    removedSmallBarriersGainMiles: PropTypes.number,
    removedSmallBarriersByYear: PropTypes.string,
    crossings: PropTypes.number,
    miles: PropTypes.number,
  }).isRequired,
  metric: PropTypes.string.isRequired,
  onChangeMetric: PropTypes.func.isRequired,
  onClose: PropTypes.func.isRequired,
}

export default UnitDetails
