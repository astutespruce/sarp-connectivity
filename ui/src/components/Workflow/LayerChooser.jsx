import React from 'react'
import PropTypes from 'prop-types'
import { Box, Heading, Text } from 'theme-ui'

import { ToggleButton } from 'components/Button'

const adminLayerOptions = [
  { value: 'State', label: 'State' },
  { value: 'County', label: 'County' },
  { value: 'CongressionalDistrict', label: 'Congressional Districts' },
]

const hucLayerOptions = [
  { value: 'HUC6', label: 'Basin', sublabel: '(HUC6)' },
  { value: 'HUC8', label: 'Subbasin', sublabel: '(HUC8)' },
  { value: 'HUC10', label: 'Watershed', sublabel: '(HUC10)' },
  { value: 'HUC12', label: 'Subwatershed', sublabel: '(HUC12)' },
]

const otherLayerOptions = [
  { value: 'StateWRA', label: 'State Water Resource Areas' },
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
          Administrative / political unit
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
          Other units
        </Heading>
        <ToggleButton
          options={otherLayerOptions}
          onChange={handleSelectLayer}
        />
        <Text variant="help" sx={{ fontSize: 0, mt: '0.5rem' }}>
          State water resource areas currently include Washington State Water
          Resource Inventory Areas.
        </Text>
      </Box>
    </Box>
  )
}

LayerChooser.propTypes = {
  setLayer: PropTypes.func.isRequired,
}

export default LayerChooser
