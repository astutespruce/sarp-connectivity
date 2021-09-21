import React from 'react'
import PropTypes from 'prop-types'
import { Box } from 'theme-ui'
import { QuestionCircle } from '@emotion-icons/fa-regular'

import Tooltip from './Tooltip'

const InfoTooltip = ({ children, direction, ...props }) => (
  <Tooltip
    content={children}
    direction={direction}
    inline
    sx={{ fontSize: 0, maxWidth: 300 }}
    {...props}
  >
    <Box
      sx={{
        ml: '0.5em',
        cursor: 'default',
        color: 'grey.7',
        '&:hover': {
          color: 'grey.9',
        },
      }}
    >
      <QuestionCircle size="1em" />
    </Box>
  </Tooltip>
)

InfoTooltip.propTypes = {
  children: PropTypes.oneOfType([
    PropTypes.node,
    PropTypes.arrayOf(PropTypes.node),
  ]).isRequired,
  direction: PropTypes.string,
}

InfoTooltip.defaultProps = {
  direction: 'right',
}

export default InfoTooltip
