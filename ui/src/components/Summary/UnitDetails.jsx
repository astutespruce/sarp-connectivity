/* eslint-disable camelcase */
import React from 'react'
import PropTypes from 'prop-types'

import { Text, HelpText } from 'components/Text'
import { CloseButton } from 'components/Button'
import { Box, Flex } from 'components/Grid'
import { formatNumber } from 'util/format'
import styled, { themeGet } from 'style'
import { layers } from './layers'
import { STATE_FIPS, CONNECTIVITY_TEAMS } from '../../../config/constants'

const Wrapper = styled(Flex).attrs({
  flexDirection: 'column',
})`
  height: 100%;
`

const Header = styled(Flex).attrs({
  py: '1rem',
  pl: '1rem',
  pr: '0.5rem',
  justifyContent: 'center',
  alignItems: 'flex-start',
})`
  background: #f6f6f2;
  border-bottom: 1px solid #ddd;
  flex: 0;
  line-height: 1.3;
`

const TitleWrapper = styled.div`
  flex-grow: 1;
`

const Title = styled(Text).attrs({ as: 'h3', fontSize: '1.25rem', m: 0 })``

const Subtitle = styled(Text).attrs({ fontSize: '1.25rem' })``

const UnitID = styled(Text)`
  color: ${themeGet('colors.grey.700')};
`

const Content = styled(Box).attrs({
  p: '1rem',
})`
  flex: 1;
  height: 100%;
  overflow-y: auto;
`

const List = styled.ul`
  margin-top: 1rem;
`

const UnitDetails = ({ barrierType, summaryUnit, onClose }) => {
  const {
    id,
    layerId,
    name = '',
    dams = 0,
    on_network_dams = 0,
    barriers = 0,
    on_network_barriers = 0,
    total_barriers = 0,
    crossings = 0,
    miles = 0,
  } = summaryUnit

  const totalRoadBarriers = total_barriers + crossings
  const offNetworkDams = dams - on_network_dams
  const offNetworkBarriers = barriers - on_network_barriers

  const layerConfig = layers.filter(({ id: lyrID }) => lyrID === layerId)[0]
  let { title: layerTitle } = layerConfig

  let title = name || id
  if (layerId === 'County') {
    title = `${name} County`
    layerTitle = STATE_FIPS[id.slice(0, 2)]
  }

  let team = null
  if (layerId === 'State') {
    team = CONNECTIVITY_TEAMS[id]
  }

  return (
    <Wrapper>
      <Header
        id="SidebarHeader"
        className="flex-container flex-justify-center flex-align-start"
      >
        <TitleWrapper>
          <Title>{title}</Title>
          {layerId !== 'State' && <Subtitle>{layerTitle}</Subtitle>}
          {layerId === 'HUC6' || layerId === 'HUC8' || layerId === 'HUC12' ? (
            <UnitID>HUC: {id}</UnitID>
          ) : null}
        </TitleWrapper>
        <CloseButton onClick={onClose} />
      </Header>
      <Content>
        {barrierType === 'dams' ? (
          <>
            {dams > 0 ? (
              <>
                This area contains:
                <List>
                  <li>
                    <b>{formatNumber(dams, 0)}</b> inventoried{' '}
                    {dams > 1 ? 'dams' : 'dam'}
                  </li>
                  <li>
                    <b>{formatNumber(on_network_dams, 0)}</b>{' '}
                    {on_network_dams > 1 ? 'dams' : 'dam'} that{' '}
                    {on_network_dams > 1 ? 'were ' : 'was '} analyzed for
                    impacts to aquatic connectivity in this tool
                  </li>
                  <li>
                    <b>{formatNumber(miles, 2)}</b> miles of connected rivers
                    and streams
                  </li>
                </List>
                <HelpText>
                  <br />
                  Note: These statistics are based on <i>inventoried</i> dams.
                  Because the inventory is incomplete in many areas, areas with
                  a high number of dams may simply represent areas that have a
                  more complete inventory.
                  {offNetworkDams > 0 ? (
                    <>
                      <br />
                      <br />
                      {formatNumber(offNetworkDams, 0)}{' '}
                      {offNetworkDams > 1 ? 'dams' : 'dam'} were not analyzed
                      because they were not on the aquatic network or could not
                      be correctly located on the network.
                    </>
                  ) : null}
                </HelpText>
              </>
            ) : (
              <HelpText>
                This area does not yet have any inventoried dams
              </HelpText>
            )}
            {team ? (
              <div style={{ marginTop: '3rem' }}>
                <h5 className="title is-5" style={{ marginBottom: '0.5em' }}>
                  Aquatic Connectivity Team
                </h5>
                <p>
                  {team.description}
                  <br />
                  <br />
                  For more information, please contact{' '}
                  <a href={`mailto:${team.contact.email}`}>
                    {team.contact.name}
                  </a>
                  .
                </p>
              </div>
            ) : null}
          </>
        ) : (
          <>
            {totalRoadBarriers > 0 ? (
              <>
                This area contains:
                <List>
                  <li>
                    <b>{formatNumber(totalRoadBarriers, 0)}</b> road-related
                    potential {totalRoadBarriers > 1 ? 'barriers' : 'barrier'}
                  </li>
                  <li>
                    <b>{formatNumber(total_barriers, 0)}</b>{' '}
                    {total_barriers > 1 ? 'barriers' : 'barrier'}
                    {total_barriers > 1 ? 'have ' : 'has '} been assessed for
                    impacts to aquatic organisms.
                  </li>
                  <li>
                    <b>{formatNumber(barriers, 0)}</b> road-related{' '}
                    {barriers > 1 ? 'barriers' : 'barrier'} assessed{' '}
                    {barriers > 1 ? 'are' : 'is'} likely to impact aquatic
                    organisms
                  </li>
                  <li>
                    <b>{formatNumber(on_network_barriers, 0)}</b>{' '}
                    {on_network_barriers > 1 ? 'dams' : 'dam'} that{' '}
                    {on_network_barriers > 1 ? 'were ' : 'was '} analyzed for
                    impacts to aquatic connectivity in this tool
                  </li>
                </List>
                <HelpText>
                  <br />
                  <br />
                  Note: These statistics are based on <i>inventoried</i>{' '}
                  road-related barriers that have been assessed for impacts to
                  aquatic organisms. Because the inventory is incomplete in many
                  areas, areas with a high number of barriers may simply
                  represent areas that have a more complete inventory.
                  {offNetworkBarriers > 0 ? (
                    <>
                      <br />
                      <br />
                      {formatNumber(offNetworkBarriers, 0)}{' '}
                      {offNetworkBarriers > 1 ? 'barriers' : 'barrier'} that{' '}
                      {offNetworkBarriers > 1 ? 'were ' : 'was '} not analyzed
                      because they were not on the aquatic network or could not
                      be correctly located on the network
                    </>
                  ) : null}
                </HelpText>
              </>
            ) : (
              <HelpText>
                This area does not yet have any road-related barriers that have
                been assessed for impacts to aquatic organisms.
              </HelpText>
            )}
          </>
        )}
      </Content>
    </Wrapper>
  )
}

UnitDetails.propTypes = {
  barrierType: PropTypes.string.isRequired,
  summaryUnit: PropTypes.shape({
    id: PropTypes.oneOfType([PropTypes.string, PropTypes.number]).isRequired,
    layerId: PropTypes.string.isRequired,
    name: PropTypes.string,
    dams: PropTypes.number,
    on_network_dams: PropTypes.number,
    barriers: PropTypes.number,
    total_barriers: PropTypes.number,
    on_network_barriers: PropTypes.number,
    crossings: PropTypes.number,
    miles: PropTypes.number,
  }).isRequired,
  onClose: PropTypes.func.isRequired,
}

export default UnitDetails
