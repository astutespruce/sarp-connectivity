import React from 'react'
import PropTypes from 'prop-types'
import { Box, Heading, Text } from 'theme-ui'

import {
  FISH_HABITAT_PARTNERSHIPS,
  STATES,
  TNC_COLDWATER_STATUS,
  TNC_RESILIENCE,
  TU_BROOK_TROUT_PORTFOLIO,
} from 'config'
import { OutboundLink } from 'components/Link'
import { Entry } from './elements'

const LandscapeContext = ({
  brooktroutportfolio,
  cold,
  congressionaldistrict,
  ejtract,
  ejtribal,
  fishhabitatpartnership,
  nativeterritories,
  resilience,
  sx,
}) => (
  <Box sx={sx}>
    <Heading as="h3">Landscape context</Heading>

    {cold ? (
      <Entry>
        Ability of the watershed to maintain cold water habitat:{' '}
        {TNC_COLDWATER_STATUS[cold]}
        <Text sx={{ fontSize: 0, color: 'grey.7', lineHeight: 1.1 }}>
          based on The Nature Conservancy&apos;s cold water temperature score
          where this barrier occurs (TNC; March 2024).
        </Text>
      </Entry>
    ) : null}

    {resilience ? (
      <Entry>
        Freshwater resilience: {TNC_RESILIENCE[resilience]}
        <Text sx={{ fontSize: 0, color: 'grey.7', lineHeight: 1.1 }}>
          based on the The Nature Conservancy&apos;s freshwater resilience
          category of the watershed where this barrier occurs (v0.44).
        </Text>
      </Entry>
    ) : null}

    {brooktroutportfolio ? (
      <Entry>
        Eastern brook trout conservation portfolio:{' '}
        {TU_BROOK_TROUT_PORTFOLIO[brooktroutportfolio]}
        <Text sx={{ fontSize: 0, color: 'grey.7', lineHeight: 1.1 }}>
          based on the{' '}
          <OutboundLink to="https://www.tu.org/science/conservation-planning-and-assessment/conservation-portfolio/">
            brook trout conservation portfolio
          </OutboundLink>{' '}
          category of the watershed where this barrier occurs, as identified by
          Trout Unlimited (7/4/2022).
        </Text>
      </Entry>
    ) : null}

    {ejtract || ejtribal ? (
      <Entry>
        Climate and environmental justice:{' '}
        {ejtract ? 'within a disadvantaged census tract' : null}
        {ejtract && ejtribal ? ', ' : null}
        {ejtribal ? 'within a tribal community' : null}
      </Entry>
    ) : null}

    {nativeterritories ? (
      <Entry>
        <Text>
          Within the following native territories: {nativeterritories}
        </Text>
        <Text sx={{ fontSize: 0, color: 'grey.7', lineHeight: 1.1 }}>
          based on data provided by{' '}
          <OutboundLink to="https://native-land.ca/">
            Native Land Digital
          </OutboundLink>
          .
        </Text>
      </Entry>
    ) : null}

    {congressionaldistrict ? (
      <Entry>
        Congressional district (118th congress):{' '}
        {STATES[congressionaldistrict.slice(0, 2)]} Congressional District{' '}
        {congressionaldistrict.slice(2)}
      </Entry>
    ) : null}

    {fishhabitatpartnership ? (
      <Entry>
        <Text>Fish Habitat Partnerships working in this area:</Text>
        <Text sx={{ mt: '0.25rem', ml: '1rem' }}>
          {fishhabitatpartnership.split(',').map((code, i) => (
            <React.Fragment key={code}>
              {i > 0 ? ', ' : null}
              <OutboundLink to={FISH_HABITAT_PARTNERSHIPS[code].url}>
                {FISH_HABITAT_PARTNERSHIPS[code].name}
              </OutboundLink>
            </React.Fragment>
          ))}
        </Text>
      </Entry>
    ) : null}
  </Box>
)

LandscapeContext.propTypes = {
  brooktroutportfolio: PropTypes.number,
  cold: PropTypes.number,
  congressionaldistrict: PropTypes.string,
  ejtract: PropTypes.bool,
  ejtribal: PropTypes.bool,
  fishhabitatpartnership: PropTypes.string,
  nativeterritories: PropTypes.string,
  resilience: PropTypes.number,
  sx: PropTypes.object,
}

LandscapeContext.defaultProps = {
  brooktroutportfolio: null,
  cold: null,
  congressionaldistrict: null,
  ejtract: false,
  ejtribal: false,
  fishhabitatpartnership: null,
  nativeterritories: null,
  resilience: null,
  sx: null,
}

export default LandscapeContext
