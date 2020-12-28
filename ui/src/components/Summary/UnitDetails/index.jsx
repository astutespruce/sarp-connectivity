/* eslint-disable camelcase */
import React from 'react'
import PropTypes from 'prop-types'

import { Text } from 'components/Text'
import { OutboundLink } from 'components/Link'
import { CloseButton } from 'components/Button'
import { Box, Flex } from 'components/Grid'
import { Downloader } from 'components/Download'
import styled, { themeGet } from 'style'
import { layers } from '../layers'
import Barriers from './Barriers'
import Dams from './Dams'
import { STATE_FIPS, CONNECTIVITY_TEAMS } from '../../../../config/constants'

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
  flex: 0 0 auto;
  line-height: 1.3;
`

const Footer = styled(Flex).attrs({
  justifyContent: 'flex-end',
  p: '1rem',
})`
  flex-grow: 0 0 auto;
  border-top: 1px solid #ddd;
  background: #f6f6f2;
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

const UnitDetails = ({ barrierType, summaryUnit, onClose }) => {
  const { id, layerId, name = '', dams = 0, total_barriers = 0 } = summaryUnit

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

  const hasBarriers = barrierType === 'dams' ? dams > 0 : total_barriers > 0
  const downloaderConfig = {
    layer: layerId,
    summaryUnits: [{ id }],
    scenario: 'ncwc',
  }

  return (
    <Wrapper>
      <Header id="SidebarHeader">
        <TitleWrapper>
          <Title>{title}</Title>
          {layerId !== 'State' && <Subtitle>{layerTitle}</Subtitle>}
          {layerId === 'HUC6' || layerId === 'HUC8' || layerId === 'HUC12' ? (
            <UnitID>
              {layerId}: {id}
            </UnitID>
          ) : null}
        </TitleWrapper>
        <CloseButton onClick={onClose} />
      </Header>
      <Content>
        {barrierType === 'dams' ? (
          <Dams {...summaryUnit} />
        ) : (
          <Barriers {...summaryUnit} />
        )}

        {team ? (
          <div style={{ marginTop: '3rem' }}>
            <h5 style={{ marginBottom: '0.5em' }}>
              {title} Aquatic Connectivity Team
            </h5>
            <p>
              {team.description}
              <br />
              <br />
              {team.url !== undefined ? (
                <>
                  Please see the{' '}
                  <OutboundLink to={team.url}>
                    {title} Aquatic Connectivity Team website
                  </OutboundLink>
                  .
                  <br />
                  <br />
                </>
              ) : null}
              For more information, please contact{' '}
              <a href={`mailto:${team.contact.email}`}>{team.contact.name}</a> (
              {team.contact.org}).
            </p>
          </div>
        ) : null}
      </Content>

      {hasBarriers ? (
        <Footer>
          <Downloader barrierType={barrierType} config={downloaderConfig} />
        </Footer>
      ) : null}
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
