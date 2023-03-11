import React from 'react'
import PropTypes from 'prop-types'
import { Box } from 'theme-ui'

import { getLegendEntries } from 'components/Report/Legend'
import LegendElement from './LegendElement'

const Legend = ({ networkType, name, visibleLayers }) => {
  const entries = getLegendEntries({ networkType, name, visibleLayers })

  return (
    <Box
      sx={{
        fontSize: 1,
        '> div + div': {
          mt: '0.5em',
        },
      }}
    >
      {entries.map((entry, i) => (
        <LegendElement
          key={entry.label}
          sx={{ fontWeight: i === 0 ? 'bold' : 'inherit' }}
          {...entry}
        />
      ))}
    </Box>
  )
}

Legend.propTypes = {
  networkType: PropTypes.string.isRequired,
  name: PropTypes.string.isRequired,
  visibleLayers: PropTypes.object, // Set()
}

Legend.defaultProps = {
  visibleLayers: null,
}

export default Legend
