import React from 'react'
import PropTypes from 'prop-types'
import { Text, Link } from '@react-pdf/renderer'

import {
  FISH_HABITAT_PARTNERSHIPS,
  STATES,
  TNC_COLDWATER_STATUS,
  TNC_RESILIENCE,
  TU_BROOK_TROUT_PORTFOLIO,
} from 'config'

import { Entry, Entries, Section } from './elements'

const LandscapeContext = ({
  brooktroutportfolio,
  cold,
  congressionaldistrict,
  ejtract,
  ejtribal,
  fishhabitatpartnership,
  nativeterritories,
  resilience,
  ...props
}) => (
  <Section title="Landscape context" {...props} wrap={false}>
    <Entries>
      {cold ? (
        <Entry>
          <Text>
            Ability of the watershed to maintain cold water habitat:{' '}
            {TNC_COLDWATER_STATUS[cold]}
          </Text>
          <Text style={{ fontSize: '10pt', color: '#7f8a93', lineHeight: 1.1 }}>
            based on The Nature Conservancy&apos;s cold water temperature score
            where this barrier occurs (TNC; March 2024).
          </Text>
        </Entry>
      ) : null}

      {resilience ? (
        <Entry>
          <Text>Freshwater resilience: {TNC_RESILIENCE[resilience]}</Text>
          <Text style={{ fontSize: '10pt', color: '#7f8a93', lineHeight: 1.1 }}>
            based on the The Nature Conservancy&apos;s freshwater resilience
            category of the watershed where this barrier occurs (v0.44).
          </Text>
        </Entry>
      ) : null}

      {brooktroutportfolio ? (
        <Entry>
          <Text>
            Eastern brook trout conservation portfolio:{' '}
            {TU_BROOK_TROUT_PORTFOLIO[brooktroutportfolio]}
          </Text>
          <Text style={{ fontSize: '10pt', color: '#7f8a93', lineHeight: 1.1 }}>
            based on the{' '}
            <Link href="https://www.tu.org/science/conservation-planning-and-assessment/conservation-portfolio/">
              brook trout conservation portfolio
            </Link>{' '}
            category of the watershed where this barrier occurs, as identified
            by Trout Unlimited (7/4/2022).
          </Text>
        </Entry>
      ) : null}

      {ejtract || ejtribal ? (
        <Entry>
          <Text>
            Climate and environmental justice:{' '}
            {ejtract ? 'within a disadvantaged census tract' : null}
            {ejtract && ejtribal ? ', ' : null}
            {ejtribal ? 'within a tribal community' : null}
          </Text>
        </Entry>
      ) : null}

      {nativeterritories ? (
        <Entry>
          <Text>Within the following native territories:</Text>
          <Text style={{ marginTop: '6pt' }}>{nativeterritories}</Text>
          <Text style={{ fontSize: '10pt', color: '#7f8a93', lineHeight: 1.1 }}>
            Note: fonts for native territories may not render properly; our
            apologies, no disrespect is intended.
          </Text>
          <Text style={{ fontSize: '10pt', color: '#7f8a93', lineHeight: 1.1 }}>
            based on data provided by{' '}
            <Link href="https://native-land.ca/">Native Land Digital</Link>
          </Text>
        </Entry>
      ) : null}

      {congressionaldistrict ? (
        <Entry>
          <Text>
            Congressional district: {STATES[congressionaldistrict.slice(0, 2)]}{' '}
            (118th congress) Congressional District{' '}
            {congressionaldistrict.slice(2)}
          </Text>
        </Entry>
      ) : null}

      {fishhabitatpartnership ? (
        <Entry>
          <Text>Fish Habitat Partnerships working in this area:</Text>
          <Text sx={{ mt: '0.25rem', ml: '1rem' }}>
            {fishhabitatpartnership.split(',').map((code, i) => (
              <React.Fragment key={code}>
                {i > 0 ? ', ' : null}
                <Link href={FISH_HABITAT_PARTNERSHIPS[code].url}>
                  {FISH_HABITAT_PARTNERSHIPS[code].name}
                </Link>
              </React.Fragment>
            ))}
          </Text>
        </Entry>
      ) : null}
    </Entries>
  </Section>
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
}

export default LandscapeContext
