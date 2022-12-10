/* eslint-disable camelcase */

import React from 'react'
import PropTypes from 'prop-types'
import { Text, View } from '@react-pdf/renderer'

import { RECON } from 'config'
import { Section } from './elements'

const Feasibility = ({ recon, ...props }) => (
  <Section title="Feasibility & conservation benefit" {...props} wrap={false}>
    <View>
      {recon !== null ? (
        <Text>{RECON[recon]}.</Text>
      ) : (
        <Text>No feasibility information is available for this barrier.</Text>
      )}
    </View>
  </Section>
)

Feasibility.propTypes = {
  recon: PropTypes.number,
}

Feasibility.defaultProps = {
  recon: 0,
}

export default Feasibility
