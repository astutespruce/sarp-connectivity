import React from 'react'
import PropTypes from 'prop-types'
import { Flex, Text } from 'theme-ui'

import LegendSymbol from './LegendSymbol'

const LegendElement = ({ label, ...props }) => (
  <Flex sx={{}}>
    <LegendSymbol {...props} />
    <Text sx={{ ml: '0.5rem' }}>{label}</Text>
  </Flex>
)

LegendElement.propTypes = {
  label: PropTypes.string.isRequired,
}

export default LegendElement
