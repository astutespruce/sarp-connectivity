import React from 'react'
import PropTypes from 'prop-types'
import { Text } from '@react-pdf/renderer'

import Flex from './Flex'
import LegendSymbol from './LegendSymbol'

const LegendElement = ({ label, ...props }) => (
  <Flex style={{ marginBottom: 4 }}>
    <LegendSymbol {...props} />
    <Text style={{ flex: '1 1 auto', fontSize: 10 }}>{label}</Text>
  </Flex>
)

LegendElement.propTypes = {
  label: PropTypes.string.isRequired,
}

export default LegendElement
