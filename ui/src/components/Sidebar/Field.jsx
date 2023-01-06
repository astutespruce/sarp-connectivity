import React from 'react'
import PropTypes from 'prop-types'
import { Box, Flex, Text } from 'theme-ui'

const defaultCSS = { textAlign: 'right' }
const unknownCSS = { fontSize: 0, color: 'grey.6', textAlign: 'right' }

const Entry = ({ label, children, isUnknown, sx }) => (
  <Flex sx={{ justifyContent: 'space-between', alignItems: 'baseline', ...sx }}>
    <Text
      sx={{
        mr: '0.5em',
        flex: '1 1 auto',
        maxWidth: '80%',
        fontSize: 1,
      }}
    >
      {label}:
    </Text>
    <Box sx={isUnknown ? unknownCSS : defaultCSS}>{children}</Box>
  </Flex>
)

Entry.propTypes = {
  label: PropTypes.string.isRequired,
  children: PropTypes.oneOfType([
    PropTypes.node,
    PropTypes.arrayOf(PropTypes.node),
  ]).isRequired,
  isUnknown: PropTypes.bool,
  sx: PropTypes.object,
}

Entry.defaultProps = {
  isUnknown: false,
  sx: {},
}

export default Entry
