import React from 'react'
import PropTypes from 'prop-types'
import { Box, Text } from 'theme-ui'

import { SALMONID_ESU, TROUT, barrierTypeLabelSingular } from 'config'
import { Entry, Field } from 'components/Sidebar'
import {
  SpeciesWatershedPresencePropTypeStub,
  SpeciesWatershedPresenceDefaultProps,
} from './proptypes'

const presentCSS = {
  fontSize: 1,
  fontWeight: 'bold',
}

const absentCSS = {
  fontSize: 1,
  color: 'grey.7',
}

const SpeciesInfo = ({
  barrierType,
  tespp,
  regionalsgcnspp,
  statesgcnspp,
  trout,
  salmonidesu,
}) => {
  const typeLabel = barrierTypeLabelSingular[barrierType]

  const disclaimer = (
    <Entry>
      <Text variant="help" sx={{ mt: '1rem', fontSize: 0 }}>
        Note: species information is very incomplete and is limited to the
        subwatershed level. These species may or may not be directly impacted by
        this {typeLabel}.{' '}
        <a href="/sgcn" target="_blank">
          Read more.
        </a>
      </Text>
    </Entry>
  )

  if (!(tespp + regionalsgcnspp + statesgcnspp > 0 || trout || salmonidesu)) {
    return (
      <>
        <Text
          variant="help"
          sx={{
            my: '0.5rem',
            mr: '0.5rem',
            px: '0.5rem',
          }}
        >
          Data sources in the subwatershed containing this {typeLabel} have not
          recorded any federally-listed threatened and endangered aquatic
          species, state-listed aquatic Species of Greatest Conservation Need,
          regionally-listed aquatic Species of Greatest Conservation Need, trout
          species, or salmon ESU / steelhead trout DPS.
        </Text>
        {disclaimer}
      </>
    )
  }

  return (
    <>
      <Entry>
        <Field label="Number of federally-listed threatened and endangered aquatic species">
          <Text sx={tespp > 0 ? presentCSS : absentCSS}>{tespp}</Text>
        </Field>
      </Entry>
      <Entry>
        <Field
          label="Number of state-listed aquatic Species of Greatest
          Conservation Need (including state-listed threatened and
          endangered species)"
        >
          <Text sx={statesgcnspp > 0 ? presentCSS : absentCSS}>
            {statesgcnspp}
          </Text>
        </Field>
      </Entry>
      <Entry>
        <Field
          label="Number of regionally-listed aquatic Species of Greatest
          Conservation Need"
        >
          <Text sx={regionalsgcnspp > 0 ? presentCSS : absentCSS}>
            {regionalsgcnspp}
          </Text>
        </Field>
      </Entry>
      <Entry>
        <Field label="Trout species present">
          {trout ? (
            <Text sx={{ fontSize: 1 }}>
              {trout
                .split(',')
                .map((code) => TROUT[code])
                .join(', ')}
            </Text>
          ) : (
            <Text sx={absentCSS}>none recorded</Text>
          )}
        </Field>
      </Entry>
      {salmonidesu ? (
        <Entry>
          <Field
            label="Salmon Evolutionarily Significant Units / Steelhead trout Discrete Population Segments present"
            sx={{
              display: 'block',
              '&>div': {
                mt: '0.25rem',
                ml: '2rem',
                textAlign: 'left',
              },
              '& li+li': {
                mt: '0.25rem',
              },
            }}
          >
            <Box as="ul">
              {salmonidesu.split(',').map((code) => (
                <li key={code}>{SALMONID_ESU[code]}</li>
              ))}
            </Box>
          </Field>
        </Entry>
      ) : null}
      {disclaimer}
    </>
  )
}

SpeciesInfo.propTypes = {
  barrierType: PropTypes.string.isRequired,
  ...SpeciesWatershedPresencePropTypeStub,
}

SpeciesInfo.defaultProps = SpeciesWatershedPresenceDefaultProps

export default SpeciesInfo
