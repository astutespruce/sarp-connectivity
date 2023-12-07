/* eslint-disable camelcase */
import React from 'react'
import PropTypes from 'prop-types'
import { Box, Button, Heading, Flex, Text, Paragraph } from 'theme-ui'
import { AngleDoubleRight } from '@emotion-icons/fa-solid'

import { Link, ExternalLink } from 'components/Link'
import { Downloader } from 'components/Download'
import {
  STATE_FIPS,
  STATES,
  CONNECTIVITY_TEAMS,
  barrierTypeLabels,
} from 'config'
import { formatNumber, pluralize } from 'util/format'

import { layers } from './layers'

const UnitDetails = ({ barrierType, summaryUnit, onClose }) => {
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
    rankedDams = 0,
    removedDams = 0,
    removedDamsGainMiles = 0,
    smallBarriers = 0,
    totalSmallBarriers = 0,
    rankedSmallBarriers = 0,
    removedSmallBarriers = 0,
    removedSmallBarriersGainMiles = 0,
    crossings = 0,
  } = summaryUnit

  const unrankedDams = dams - rankedDams
  const unrankedBarriers = smallBarriers - rankedSmallBarriers
  const totalRoadBarriers = totalSmallBarriers + crossings

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

  const downloaderConfig = {
    layer: layerId,
    summaryUnits: [{ id }],
    scenario: 'ncwc',
  }

  let downloadButtons = null

  switch (barrierType) {
    case 'dams': {
      downloadButtons = (
        <Box sx={{ width: '10rem' }}>
          <Flex sx={{ ml: '1rem', flex: '1 1 auto' }}>
            <Downloader
              barrierType="dams"
              label={barrierTypeLabels.dams}
              config={downloaderConfig}
              disabled={dams === 0}
            />
          </Flex>
        </Box>
      )

      break
    }
    case 'small_barriers': {
      downloadButtons = (
        <Flex sx={{ justifyContent: 'space-between', gap: '1rem' }}>
          <Downloader
            barrierType="small_barriers"
            label={barrierTypeLabels.small_barriers}
            config={downloaderConfig}
            disabled={totalSmallBarriers === 0}
          />

          <Downloader
            barrierType="road_crossings"
            label={barrierTypeLabels.road_crossings}
            config={{
              layer: layerId,
              summaryUnits: [{ id }],
            }}
            disabled={crossings === 0}
          />
        </Flex>
      )
      break
    }
    case 'combined_barriers': {
      downloadButtons = (
        <Flex sx={{ justifyContent: 'space-between', gap: '1rem' }}>
          <Downloader
            barrierType="dams"
            label={barrierTypeLabels.dams}
            config={downloaderConfig}
            disabled={dams === 0}
          />
          <Downloader
            barrierType="small_barriers"
            label={barrierTypeLabels.small_barriers}
            config={downloaderConfig}
            disabled={totalSmallBarriers === 0}
          />
        </Flex>
      )
      break
    }
    default: {
      break
    }
  }

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
        {layerId === 'State' ? (
          <Box sx={{ mt: '-0.5rem', mb: '1rem' }}>
            <Link to={`/states/${id}`}>
              view state page for more information{' '}
              <AngleDoubleRight size="1em" />
            </Link>
          </Box>
        ) : null}

        <Paragraph>This area contains:</Paragraph>

        {barrierType === 'dams' || barrierType === 'combined_barriers' ? (
          <>
            {dams > 0 ? (
              <>
                <Paragraph sx={{ mt: '0.5rem' }}>
                  <b>{formatNumber(dams, 0)}</b> inventoried{' '}
                  {dams === 1 ? 'dam' : 'dams'}, including:
                </Paragraph>

                <Box as="ul" sx={{ mt: '0.5rem' }}>
                  <li>
                    <b>{formatNumber(rankedDams, 0)}</b> that{' '}
                    {rankedDams === 1 ? 'was ' : 'were '} analyzed for impacts
                    to aquatic connectivity in this tool
                  </li>
                  {removedDams > 0 ? (
                    <li>
                      <b>{formatNumber(removedDams, 0)}</b> that have been
                      removed or mitigated, gaining{' '}
                      <b>{formatNumber(removedDamsGainMiles)} miles</b> of
                      reconnected rivers and streams
                    </li>
                  ) : null}
                </Box>
              </>
            ) : (
              <Text sx={{ mt: '0.5rem' }}>
                <b>0</b> inventoried dams
              </Text>
            )}
          </>
        ) : null}

        {barrierType === 'small_barriers' ||
        barrierType === 'combined_barriers' ? (
          <>
            {totalRoadBarriers > 0 ? (
              <>
                <Paragraph
                  sx={{
                    mt:
                      barrierType === 'combined_barriers' ? '1.5rem' : '0.5rem',
                  }}
                >
                  <b>{formatNumber(totalSmallBarriers + crossings, 0)}</b> or
                  more potential road-related aquatic barriers, including:
                </Paragraph>
                <Box as="ul" sx={{ mt: '0.5rem' }}>
                  <li>
                    <b>{formatNumber(totalRoadBarriers, 0)}</b> road/stream
                    crossings
                  </li>
                  <li>
                    <b>{formatNumber(totalSmallBarriers, 0)}</b> that{' '}
                    {totalSmallBarriers === 1 ? 'has ' : 'have '} been assessed
                    for impacts to aquatic organisms.
                  </li>
                  <li>
                    <b>{formatNumber(smallBarriers, 0)}</b> that{' '}
                    {smallBarriers === 1 ? 'is' : 'are'} likely to impact
                    aquatic organisms
                  </li>
                  <li>
                    <b>{formatNumber(rankedSmallBarriers, 0)}</b> that{' '}
                    {rankedSmallBarriers === 1 ? 'was ' : 'were '} analyzed for
                    impacts to aquatic connectivity in this tool
                  </li>
                  {removedSmallBarriers > 0 ? (
                    <li>
                      <b>{formatNumber(removedSmallBarriers, 0)}</b> that have
                      been removed or mitigated, gaining{' '}
                      <b>{formatNumber(removedSmallBarriersGainMiles)} miles</b>{' '}
                      of reconnected rivers and streams
                    </li>
                  ) : null}
                </Box>
              </>
            ) : (
              <Text sx={{ mt: '0.5rem' }}>
                <b>0</b> known road-related barriers or road/stream crossings
              </Text>
            )}
          </>
        ) : null}

        {barrierType === 'dams' ? (
          <Paragraph variant="help" sx={{ mt: '2rem' }}>
            Note: These statistics are based on <i>inventoried</i> dams. Because
            the inventory is incomplete in many areas, areas with a high number
            of dams may simply represent areas that have a more complete
            inventory.
            {unrankedDams > 0 ? (
              <>
                <br />
                <br />
                {formatNumber(unrankedDams, 0)} {pluralize('dam', unrankedDams)}{' '}
                {unrankedDams === 1 ? 'was' : 'were'} not analyzed because{' '}
                {unrankedDams === 1 ? 'it was' : 'they were'} not on the aquatic
                network or could not be correctly located on the network.
              </>
            ) : null}
          </Paragraph>
        ) : null}

        {barrierType === 'small_barriers' ? (
          <Paragraph variant="help" sx={{ mt: '2rem' }}>
            Note: These statistics are based on <i>inventoried</i> road-related
            barriers that have been assessed for impacts to aquatic organisms.
            Because the inventory is incomplete in many areas, areas with a high
            number of barriers may simply represent areas that have a more
            complete inventory.
            {unrankedBarriers > 0 ? (
              <>
                <br />
                <br />
                {formatNumber(unrankedBarriers, 0)} road-related{' '}
                {pluralize('barrier', unrankedBarriers)}{' '}
                {unrankedBarriers === 1 ? 'was' : 'were'} not analyzed because{' '}
                {unrankedBarriers === 1 ? 'it was' : 'they were'} not on the
                aquatic network or could not be correctly located on the network
              </>
            ) : null}
          </Paragraph>
        ) : null}

        {barrierType === 'combined_barriers' ? (
          <Paragraph variant="help" sx={{ mt: '2rem' }}>
            Note: These statistics are based on <i>inventoried</i> dams and
            road-related barriers that have been assessed for impacts to aquatic
            organisms. Because the inventory is incomplete in many areas, areas
            with a high number of barriers may simply represent areas that have
            a more complete inventory.
            {unrankedDams > 0 || unrankedBarriers > 0 ? (
              <>
                <br />
                <br />
                {unrankedDams > 0
                  ? `${formatNumber(unrankedDams, 0)} dams`
                  : null}
                {unrankedDams > 0 && unrankedBarriers > 0 ? ' and ' : null}
                {unrankedBarriers > 0
                  ? `${formatNumber(unrankedBarriers, 0)} road-related barriers`
                  : null}{' '}
                {unrankedDams + unrankedBarriers === 1 ? 'was' : 'were'} not
                analyzed because{' '}
                {unrankedDams + unrankedBarriers === 1 ? 'it was' : 'they were'}{' '}
                not on the aquatic network or could not be correctly located on
                the network
              </>
            ) : null}
          </Paragraph>
        ) : null}

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

      <Box
        sx={{
          flex: '0 0 auto',
          display:
            barrierType === 'dams' || barrierType === 'combined_barriers'
              ? 'flex'
              : null,
          alignItems: 'center',
          pt: '0.5rem',
          px: '1rem',
          pb: '1rem',
          borderTop: '1px solid #DDD',
          bg: '#f6f6f2',
          '& button': {
            fontSize: 1,
            textAlign: 'left',
            p: '0.5rem',
          },
        }}
      >
        <Text sx={{ lineHeight: 1, flex: '0 0 auto' }}>Download:</Text>
        <Flex
          sx={{
            flex: '1 1 auto',
            mt: '0.5rem',
            justifyContent:
              barrierType === 'small_barriers' ? 'center' : 'flex-end',
          }}
        >
          {downloadButtons}
        </Flex>
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
    smallBarriers: PropTypes.number,
    totalSmallBarriers: PropTypes.number,
    rankedSmallBarriers: PropTypes.number,
    removedSmallBarriers: PropTypes.number,
    removedSmallBarriersGainMiles: PropTypes.number,
    crossings: PropTypes.number,
    miles: PropTypes.number,
  }).isRequired,
  onClose: PropTypes.func.isRequired,
}

export default UnitDetails
