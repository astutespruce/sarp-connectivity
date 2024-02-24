import React from 'react'
import PropTypes from 'prop-types'
import { Text, View } from '@react-pdf/renderer'

import { barrierTypeLabelSingular } from 'config'
import { Section } from './elements'

const InvasiveSpecies = ({
  barrierType,
  invasive,
  invasivenetwork,
  ...props
}) => {
  const barrierTypeLabel = barrierTypeLabelSingular[barrierType]

  return (
    <Section title="Invasive species management" {...props} wrap={false}>
      <View>
        {!invasive && invasivenetwork === 1 ? (
          <Text>
            Upstream of a barrier identified as a beneficial to restricting the
            movement of invasive species.
          </Text>
        ) : null}

        {invasive ? (
          <Text>
            Note: this {barrierTypeLabel} is identified as a beneficial to
            restricting the movement of invasive species.
          </Text>
        ) : null}
      </View>
    </Section>
  )
}

InvasiveSpecies.propTypes = {
  barrierType: PropTypes.string.isRequired,
  invasive: PropTypes.bool,
  invasivenetwork: PropTypes.number,
  sx: PropTypes.object,
}

InvasiveSpecies.defaultProps = {
  invasive: 0,
  invasivenetwork: 0,
  sx: null,
}

export default InvasiveSpecies
