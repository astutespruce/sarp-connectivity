import React from 'react'
import PropTypes from 'prop-types'
import { Box, Heading, Text } from 'theme-ui'

import { ToggleButton } from 'components/Button'

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
  const handleSelectLayer = (layer) => {
    setLayer(layer)
  }

  return (
    <Box
      sx={{ flex: '1 1 auto', overflowY: 'auto', overflowX: 'auto', p: '1rem' }}
    >
      <Heading as="h3">What type of area do you want to select?</Heading>
      <Text sx={{ mt: '1rem', color: 'grey.7', fontSize: 2 }}>
        Choose from one of the following types of areas that will best capture
        your area of interest. You will select specific areas on the next
        screen.
      </Text>

      <Box sx={{ mt: '2rem' }}>
        <Heading as="h4" sx={{ mb: '0.25rem' }}>
          Administrative unit
        </Heading>
        <ToggleButton
          options={adminLayerOptions}
          onChange={handleSelectLayer}
        />
      </Box>

      <Box sx={{ mt: '3rem' }}>
        <Heading as="h4" sx={{ mb: '0.25rem' }}>
          Hydrologic unit
        </Heading>
        <ToggleButton options={hucLayerOptions} onChange={handleSelectLayer} />
      </Box>

      <Box sx={{ mt: '3rem' }}>
        <Heading as="h4" sx={{ mb: '0.25rem' }}>
          Ecoregion
        </Heading>
        <ToggleButton options={ecoLayerOptions} onChange={handleSelectLayer} />
      </Box>
    </Box>
  )
}

LayerChooser.propTypes = {
  setLayer: PropTypes.func.isRequired,
}

export default LayerChooser
