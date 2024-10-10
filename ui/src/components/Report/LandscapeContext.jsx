import React from 'react'
import PropTypes from 'prop-types'
import { Text, Link } from '@react-pdf/renderer'

import { FISH_HABITAT_PARTNERSHIPS, STATES } from 'config'

import { Entry, Entries, Section } from './elements'

const LandscapeContext = ({
  congressionaldistrict,
  ejtract,
  ejtribal,
  fishhabitatpartnership,
  nativeterritories,
  ...props
}) => (
  <Section title="Landscape context" {...props} wrap={false}>
    <Entries>
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
          <Text style={{ fontSize: '10pt', color: '#7f8a93' }}>
            Note: fonts for native territories may not render properly; our
            apologies, no disrespect is intended.
          </Text>
          <Text style={{ fontSize: '10pt', color: '#7f8a93' }}>
            (based on data provided by{' '}
            <Link href="https://native-land.ca/">Native Land Digital</Link>)
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
  congressionaldistrict: PropTypes.string,
  ejtract: PropTypes.bool,
  ejtribal: PropTypes.bool,
  fishhabitatpartnership: PropTypes.string,
  nativeterritories: PropTypes.string,
}

LandscapeContext.defaultProps = {
  congressionaldistrict: null,
  ejtract: false,
  ejtribal: false,
  fishhabitatpartnership: null,
  nativeterritories: null,
}

export default LandscapeContext
