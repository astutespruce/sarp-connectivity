/* eslint-disable camelcase */

import React from 'react'
import PropTypes from 'prop-types'
import { Text, View } from '@react-pdf/renderer'

import { FEASIBILITYCLASS, RECON } from 'config'
import { Section } from './elements'

const Feasibility = ({ feasibilityclass, recon, ...props }) => (
  <Section title="Feasibility & conservation benefit" {...props} wrap={false}>
    <View>
      <Text>Feasibility: {FEASIBILITYCLASS[feasibilityclass]}</Text>

      {recon !== null && recon > 0 ? (
        <Text style={{ marginTop: '8pt' }}>
          Field recon notes: {RECON[recon]}
        </Text>
      ) : null}
    </View>
  </Section>
)

Feasibility.propTypes = {
  feasibilityclass: PropTypes.number,
  recon: PropTypes.number,
}

Feasibility.defaultProps = {
  feasibilityclass: 0,
  recon: 0,
}

export default Feasibility
