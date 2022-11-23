import React, { useEffect, useRef, memo } from 'react'
import PropTypes from 'prop-types'
import { Box, Text } from 'theme-ui'

import { STATES } from 'config'

const ListItem = ({
  id,
  name,
  state,
  layer,
  showID,
  disabled,
  focused,
  onClick,
}) => {
  const node = useRef(null)

  useEffect(() => {
    if (node.current && focused) {
      node.current.focus()
    }
  }, [focused])

  const stateLabels = state
    ? state
        .split(',')
        .map((s) => STATES[s])
        .sort()
        .join(', ')
    : ''

  return (
    <Box
      ref={node}
      as="li"
      onClick={!disabled ? onClick : null}
      tabIndex={0}
      sx={{
        p: '0.5em',
        m: '0px',
        borderBottom: '1px solid #EEE',
        cursor: disabled ? 'not-allowed' : 'pointer',
        lineHeight: 1.2,
        '&:hover': {
          bg: 'grey.0',
        },
        fontStyle: disabled ? 'italic' : 'inherit',
        color: disabled ? 'grey.7' : 'inherit',
        bg: disabled ? 'grey.0' : 'inherit',
      }}
    >
      <Box sx={{ fontWeight: !disabled ? 'bold' : 'inherit' }}>
        {name}
        {disabled ? (
          <Text sx={{ fontSize: 0, display: 'inline-block', ml: '0.25rem' }}>
            (already selected)
          </Text>
        ) : null}
      </Box>
      {showID ? (
        <Box
          sx={{
            fontSize: 0,
            color: 'grey.7',
            whiteSpace: 'nowrap',
            wordWrap: 'none',
          }}
        >
          {layer ? `${layer}: ` : null}
          {id}
        </Box>
      ) : null}

      {stateLabels ? (
        <Text sx={{ fontSize: 1, color: 'grey.7' }}>{stateLabels}</Text>
      ) : null}
    </Box>
  )
}

ListItem.propTypes = {
  id: PropTypes.string.isRequired,
  name: PropTypes.string.isRequired,
  onClick: PropTypes.func.isRequired,
  state: PropTypes.string,
  layer: PropTypes.string,
  showID: PropTypes.bool,
  disabled: PropTypes.bool,
}

ListItem.defaultProps = {
  state: '',
  layer: '',
  showID: false,
  disabled: false,
}

export default memo(ListItem)
