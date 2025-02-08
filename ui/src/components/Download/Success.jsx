import React from 'react'
import PropTypes from 'prop-types'
import { Box, Text } from 'theme-ui'

const Success = ({ url }) => (
  <Box sx={{ mt: '1rem' }}>
    <Text>
      Your browser should have automatically started downloading your file.
      <br />
      <br />
      You can also download it directly from:{' '}
      <a href={url} download>
        here
      </a>
    </Text>

    <Text variant="help" sx={{ mt: '1rem' }}>
      Note: this link will expire in 5 minutes.
      <br />
      <br />
      If you don&apos;t see the download, please check to make sure that your
      browser did not block the download file. This may be shown whereever your
      browser indicates that it blocked pop-ups.
    </Text>
  </Box>
)

Success.propTypes = { url: PropTypes.string.isRequired }

export default Success
