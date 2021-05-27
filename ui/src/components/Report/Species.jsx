import React from 'react'
import PropTypes from 'prop-types'
import { Text } from '@react-pdf/renderer'

import { Bold, List, ListItem } from './elements'

const Species = ({ tespp, statesgcnspp, regionalsgcnspp }) => (
  <List title="Species information">
    {tespp > 0 ? (
      <>
        <ListItem>
          <Text>
            <Bold>{tespp}</Bold> federally-listed threatened and endangered
            aquatic species have been found in the subwatershed containing this
            barrier.
          </Text>
        </ListItem>
      </>
    ) : (
      <ListItem>
        <Text>
          No federally-listed threatened and endangered aquatic species have
          been identified by available data sources for this subwatershed.
        </Text>
      </ListItem>
    )}

    {statesgcnspp > 0 ? (
      <>
        <ListItem>
          <Text>
            <Bold>{statesgcnspp}</Bold> state-listed aquatic Species of Greatest
            Conservation Need (SGCN) have been found in the subwatershed
            containing this barrier. These may include state-listed threatened
            and endangered species.
          </Text>
        </ListItem>
      </>
    ) : (
      <ListItem>
        <Text>
          No state-listed aquatic Species of Greatest Conservation Need (SGCN)
          have been identified by available data sources for this subwatershed.
        </Text>
      </ListItem>
    )}

    {regionalsgcnspp > 0 ? (
      <>
        <ListItem>
          <Text>
            <Bold>{regionalsgcnspp}</Bold> regionally-listed aquatic species of
            greatest conservation need have been found in the subwatershed
            containing this barrier.
          </Text>
        </ListItem>
      </>
    ) : (
      <ListItem>
        <Text>
          No regionally-listed aquatic species of greatest conservation need
          have been identified by available data sources for this subwatershed.
        </Text>
      </ListItem>
    )}

    {tespp + statesgcnspp + regionalsgcnspp > 0 ? (
      <Text style={{ color: '#7f8a93', marginTop: 8 }}>
        Note: species information is very incomplete. These species may or may
        not be directly impacted by this barrier.
      </Text>
    ) : null}
  </List>
)

Species.propTypes = {
  tespp: PropTypes.number,
  statesgcnspp: PropTypes.number,
  regionalsgcnspp: PropTypes.number,
}

Species.defaultProps = {
  tespp: 0,
  statesgcnspp: 0,
  regionalsgcnspp: 0,
}

export default Species
