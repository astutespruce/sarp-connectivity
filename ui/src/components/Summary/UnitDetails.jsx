import React from 'react'
import PropTypes from 'prop-types'

import { useSummaryData } from 'components/Data'
import { Text, HelpText } from 'components/Text'
import {CloseButton} from 'components/Button'
import { Box, Flex } from 'components/Grid'
import { formatNumber, formatPercent } from 'util/format'
import styled, { themeGet } from 'style'
import { layers } from './config'
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

const UnitDetails = ({ summaryUnit, barrierType, onClose }) => {
  // TODO
  const { id, layerId, name, dams, barriers, miles } = summaryUnit
  const {
    dams: totalDams,
    barriers: totalBarriers,
    miles: meanConnectedMiles,
  } = useSummaryData()
  const total = barrierType === 'dams' ? totalDams : totalBarriers

  const layerConfig = layers.filter(
    ({ id: lyrID }) => lyrID === layerId
  )[0]
  let { title: layerTitle } = layerConfig

  const count = barrierType === 'dams' ? dams : barriers

  const percent = (100 * count) / total
  const milesCompare = miles - meanConnectedMiles

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
          {/* <h3 className="title is-5 no-margin">{title}</h3> */}
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
            {count > 0 ? (
              <>
                <p>
                  This area contains at least {formatNumber(count, 0)}{' '}
                  {count > 1 ? 'dams' : 'dam'} that{' '}
                  {count > 1 ? 'have ' : 'has '} been inventoried so far,
                  resulting in an average of {formatNumber(miles, 2)} miles of
                  rivers and streams that could be reconnected by removing dams.
                  <br />
                  <br />
                  This area has {formatPercent(percent)}% of the inventoried
                  dams in the Southeast and{' '}
                  {formatNumber(Math.abs(milesCompare))}{' '}
                  {milesCompare > 0 ? 'more ' : 'fewer '} miles of connected
                  river network than the average for the region.
                </p>
                <HelpText>
                  <br />
                  Note: These statistics are based on <i>inventoried</i> dams.
                  Because the inventory is incomplete in many areas, areas with
                  a high number of dams may simply represent areas that have a
                  more complete inventory.
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
            {count > 0 ? (
              <>
                <p>
                  This area contains at least {formatNumber(count, 0)}{' '}
                  road-related {count > 1 ? 'barriers' : 'barriers'} that{' '}
                  {count > 1 ? 'have' : 'has'}
                  been inventoried so far.
                </p>
                <HelpText>
                  <br />
                  <br />
                  Note: These statistics are based on <i>inventoried</i>{' '}
                  road-related barriers that have been assessed for impacts to
                  aquatic organisms. Because the inventory is incomplete in many
                  areas, areas with a high number of barriers may simply
                  represent areas that have a more complete inventory.
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
  }).isRequired,
  onClose: PropTypes.func.isRequired,
}

export default UnitDetails
