/* eslint-disable camelcase */
import React from 'react'
import PropTypes from 'prop-types'
import { Box, Button, Heading, Flex, Text } from 'theme-ui'

import { OutboundLink } from 'components/Link'
import { Downloader } from 'components/Download'
import { STATE_FIPS, STATES, CONNECTIVITY_TEAMS } from 'constants'

import { layers } from '../layers'
import Barriers from './Barriers'
import Dams from './Dams'

const UnitDetails = ({ barrierType, summaryUnit, onClose }) => {
  const teams = {}
  Object.values(CONNECTIVITY_TEAMS).forEach((region) => {
    Object.entries(region).forEach(([state, info]) => {
      teams[state] = info
    })
  })

  const { id, layerId, dams = 0, totalSmallBarriers = 0 } = summaryUnit

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

  const hasBarriers = barrierType === 'dams' ? dams > 0 : totalSmallBarriers > 0
  const downloaderConfig = {
    layer: layerId,
    summaryUnits: [{ id }],
    scenario: 'ncwc',
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
        {barrierType === 'dams' ? (
          <Dams {...summaryUnit} />
        ) : (
          <Barriers {...summaryUnit} />
        )}

        {team ? (
          <Box
            sx={{
              mt: '3rem',
              borderTop: '1px solid',
              borderTopColor: 'grey.1',
              pt: '1rem',
            }}
          >
            <Heading as="h5" style={{ marginBottom: '0.5em' }}>
              {state} Aquatic Connectivity Team
            </Heading>
            <Text sx={{ fontSize: 1 }}>
              {team.description}
              <br />
              <br />
              {team.url !== undefined ? (
                <>
                  Please see the{' '}
                  <OutboundLink to={team.url}>
                    {state} Aquatic Connectivity Team website
                  </OutboundLink>
                  .
                  <br />
                  <br />
                </>
              ) : null}
              For more information, please contact{' '}
              <a href={`mailto:${team.contact.email}`}>{team.contact.name}</a> (
              {team.contact.org}).
            </Text>
          </Box>
        ) : null}
      </Box>

      {hasBarriers ? (
        <Flex
          sx={{
            justifyContent: 'flex-end',
            p: '1rem',
            flex: '0 0 auto',
            borderTop: '1px solid #DDD',
            bg: '#f6f6f2',
          }}
        >
          <Downloader barrierType={barrierType} config={downloaderConfig} />
        </Flex>
      ) : null}
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
    smallBarriers: PropTypes.number,
    totalSmallBarriers: PropTypes.number,
    unrankedSmallBarriers: PropTypes.number,
    crossings: PropTypes.number,
    miles: PropTypes.number,
  }).isRequired,
  onClose: PropTypes.func.isRequired,
}

export default UnitDetails
