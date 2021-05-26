import React from 'react'
import PropTypes from 'prop-types'
import { Box, Text, Paragraph } from 'theme-ui'

const Species = ({ tespp, statesgcnspp, regionalsgcnspp }) => (
  <Box>
    <Text sx={{ fontWeight: 'bold', fontSize: 3 }}>Species information</Text>

    <Box as="ul" sx={{ mt: '0.5rem' }}>
      {tespp > 0 ? (
        <>
          <li>
            <b>{tespp}</b> federally-listed threatened and endangered aquatic
            species have been found in the subwatershed containing this barrier.
          </li>
        </>
      ) : (
        <li>
          No federally-listed threatened and endangered aquatic species have
          been identified by available data sources for this subwatershed.
        </li>
      )}

      {statesgcnspp > 0 ? (
        <>
          <li>
            <b>{statesgcnspp}</b> state-listed aquatic Species of Greatest
            Conservation Need (SGCN) have been found in the subwatershed
            containing this barrier. These may include state-listed threatened
            and endangered species.
          </li>
        </>
      ) : (
        <li>
          No state-listed aquatic Species of Greatest Conservation Need (SGCN)
          have been identified by available data sources for this subwatershed.
        </li>
      )}

      {regionalsgcnspp > 0 ? (
        <>
          <li>
            <b>{regionalsgcnspp}</b> regionally-listed aquatic species of
            greatest conservation need have been found in the subwatershed
            containing this barrier.
          </li>
        </>
      ) : (
        <li>
          No regionally-listed aquatic species of greatest conservation need
          have been identified by available data sources for this subwatershed.
        </li>
      )}

      {tespp + statesgcnspp + regionalsgcnspp > 0 ? (
        <Paragraph variant="help" sx={{ mt: '1rem' }}>
          Note: species information is very incomplete. These species may or may
          not be directly impacted by this barrier.
        </Paragraph>
      ) : null}
    </Box>
  </Box>
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
