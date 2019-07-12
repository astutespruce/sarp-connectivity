import React from 'react'
import PropTypes from 'prop-types'

import { Box } from 'components/Grid'
import { ToggleButton } from 'components/Button'
import { Text, HelpText } from 'components/Text'
import styled, { themeGet } from 'style'

const Wrapper = styled.div``

const Title = styled(Text).attrs({
  as: 'h3',
  fontSize: '1.5rem',
  lineHeight: 1.2,
  m: 0,
})``

const Subtitle = styled(Text).attrs({ fontSize: '1.25rem' })``

const Section = styled(Box).attrs({ my: '1rem' })``

const adminLayerOptions = [
  { value: 'State', label: 'State' },
  { value: 'County', label: 'County' },
]

const hucLayerOptions = [
  { value: 'HUC6', label: `Basin\n(HUC6)` },
  { value: 'HUC8', label: `Subbasin\n(HUC8)` },
  { value: 'HUC12', label: `Subwatershed\n(HUC12)` },
]

const ecoLayerOptions = [
  { value: 'ECO3', label: 'Level 3' },
  { value: 'ECO4', label: 'Level 4' },
]

const LayerChooser = ({ setLayer }) => {
  const handleSelectLayer = layer => {
    setLayer(layer)
  }

  return (
    <Wrapper>
      <Title>What type of area do you want to select?</Title>
      <HelpText>
        Choose from one of the following types of areas that will best capture
        your area of interest. You will select specific areas on the next
        screen.
      </HelpText>

      <Section>
        <Subtitle>Administrative unit</Subtitle>
        <ToggleButton
          options={adminLayerOptions}
          onChange={handleSelectLayer}
        />
      </Section>

      <Section>
        <Subtitle>Hydrologic unit</Subtitle>
        <ToggleButton options={hucLayerOptions} onChange={handleSelectLayer} />
      </Section>

      <Section>
        <Subtitle>Ecoregion</Subtitle>
        <ToggleButton options={ecoLayerOptions} onChange={handleSelectLayer} />
      </Section>
    </Wrapper>
  )
}

LayerChooser.propTypes = {
  setLayer: PropTypes.func.isRequired,
}

export default LayerChooser
