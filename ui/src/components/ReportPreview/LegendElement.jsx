import React from 'react'
import PropTypes from 'prop-types'
import { Flex, Text } from 'theme-ui'

import LegendSymbol from './LegendSymbol'

const LegendElement = ({ label, sx, ...props }) => (
  <Flex sx={sx}>
    <LegendSymbol {...props} />
    <Text sx={{ ml: '0.5rem' }}>{label}</Text>
  </Flex>
)

LegendElement.propTypes = {
  label: PropTypes.string.isRequired,
  sx: PropTypes.object,
}

LegendElement.defaultProps = {
  sx: null,
}

export default LegendElement
