import React from 'react'
import PropTypes from 'prop-types'
import { Box } from 'theme-ui'
import { ExclamationTriangle } from '@emotion-icons/fa-solid'
import { barrierTypeLabels } from 'config'

const Error = ({ barrierType }) => (
  <Box sx={{ width: '400px' }}>
    <Box sx={{ my: '2rem' }}>
      <ExclamationTriangle size="1em" style={{ marginRight: '0.5rem' }} />
      We&apos;re sorry, there was an error creating your download. Please try
      again. If this continues to happen, please{' '}
      <a
        href={`mailto:Kat@southeastaquatics.net?subject=Issue downloading ${barrierTypeLabels[barrierType]} from National Barrier Inventory & Prioritization Tool`}
      >
        contact us
      </a>{' '}
      and let us know.
    </Box>
  </Box>
)

Error.propTypes = {
  barrierType: PropTypes.string.isRequired,
}

export default Error
