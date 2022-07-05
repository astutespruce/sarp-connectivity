/* eslint-disable camelcase */

import React from 'react'
import PropTypes from 'prop-types'
import { Text } from '@react-pdf/renderer'

import { List, ListItem, Section } from './elements'
import { RECON, HUC8_USFS } from '../../../config/constants'

const Feasibility = ({ recon, huc8_coa, huc8_sgcn, huc8_usfs, ...props }) => (
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
      {huc8_usfs > 0 && (
        <ListItem>
          <Text>Within USFS {HUC8_USFS[huc8_usfs]} priority watershed.</Text>
        </ListItem>
      )}
      {huc8_coa > 0 && (
        <ListItem>
          <Text>Within a SARP conservation opportunity area.</Text>
        </ListItem>
      )}
      {huc8_sgcn > 0 && (
        <ListItem>
          <Text>
            Within one of the top 10 watersheds in this state based on number of
            state-listed Species of Greatest Conservation Need.
          </Text>
        </ListItem>
      )}
    </List>
  </Section>
)

Feasibility.propTypes = {
  recon: PropTypes.number,
  huc8_usfs: PropTypes.number,
  huc8_coa: PropTypes.number,
  huc8_sgcn: PropTypes.number,
}

Feasibility.defaultProps = {
  recon: 0,
  huc8_usfs: 0,
  huc8_coa: 0,
  huc8_sgcn: 0,
}

export default Feasibility
