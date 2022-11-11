/* eslint-disable camelcase */

import React from 'react'
import PropTypes from 'prop-types'
import { Text } from '@react-pdf/renderer'

import { RECON } from 'config'
import { List, ListItem, Section } from './elements'

const Feasibility = ({ recon, huc8_coa, ...props }) => (
  <Section title="Feasibility & conservation benefit" {...props} wrap={false}>
    <List>
      {recon !== null ? (
        <ListItem>
          <Text>{RECON[recon]}</Text>
        </ListItem>
      ) : (
        <ListItem>
          <Text>No feasibility information is available for this barrier.</Text>
        </ListItem>
      )}

      {/* watershed priorities */}
      {huc8_coa > 0 ? (
        <ListItem>
          <Text>Within a SARP conservation opportunity area.</Text>
        </ListItem>
      ) : null}
    </List>
  </Section>
)

Feasibility.propTypes = {
  recon: PropTypes.number,
  huc8_coa: PropTypes.number,
}

Feasibility.defaultProps = {
  recon: 0,
  huc8_coa: 0,
}

export default Feasibility
