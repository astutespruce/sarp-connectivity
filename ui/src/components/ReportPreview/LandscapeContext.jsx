import React from 'react'
import PropTypes from 'prop-types'
import { Box, Heading, Text } from 'theme-ui'

import { FISH_HABITAT_PARTNERSHIPS, STATES } from 'config'
import { OutboundLink } from 'components/Link'
import { Entry } from './elements'

const LandscapeContext = ({
  congressionaldistrict,
  ejtract,
  ejtribal,
  fishhabitatpartnership,
  nativeterritories,
  sx,
}) => (
  <Box sx={sx}>
    <Heading as="h3">Landscape context</Heading>

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
          (based on data provided by{' '}
          <OutboundLink to="https://native-land.ca/">
            Native Land Digital
          </OutboundLink>
          )
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
  congressionaldistrict: PropTypes.string,
  ejtract: PropTypes.bool,
  ejtribal: PropTypes.bool,
  fishhabitatpartnership: PropTypes.string,
  nativeterritories: PropTypes.string,
  sx: PropTypes.object,
}

LandscapeContext.defaultProps = {
  congressionaldistrict: null,
  ejtract: false,
  ejtribal: false,
  fishhabitatpartnership: null,
  nativeterritories: null,
  sx: null,
}

export default LandscapeContext
