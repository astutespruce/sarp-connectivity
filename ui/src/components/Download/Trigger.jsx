import React from 'react'
import PropTypes from 'prop-types'
import { Box, Button, Flex, Text } from 'theme-ui'
import { Download as DownloadIcon } from '@emotion-icons/fa-solid'

const Trigger = ({ label, disabled, onClick }) => (
  <Button
    onClick={onClick}
    variant={!disabled ? 'primary' : 'disabled'}
    sx={{ fontSize: '1.1em', flex: '1 1 auto' }}
  >
    <Flex sx={{ justifyContent: 'center' }}>
      <Box sx={{ mr: '0.5rem', flex: '0 0 auto' }}>
        <DownloadIcon size="1.2em" />
      </Box>
      <Text sx={{ flex: '0 1 auto' }}>{label}</Text>
    </Flex>
  </Button>
)

Trigger.propTypes = {
  label: PropTypes.string.isRequired,
  disabled: PropTypes.bool,
  onClick: PropTypes.func.isRequired,
}

Trigger.defaultProps = {
  disabled: false,
}

export default Trigger
