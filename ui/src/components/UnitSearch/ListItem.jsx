import React, { useEffect, useRef, memo } from 'react'
import PropTypes from 'prop-types'
import { Box, Text } from 'theme-ui'

import { STATES, barrierTypeLabels } from 'config'
import { formatNumber } from 'util/format'

const ListItem = ({
  barrierType,
  id,
  name,
  state,
  layer,
  ranked_dams: dams,
  ranked_small_barriers: smallBarriers,
  crossings,
  showID,
  showCount,
  disabled,
  focused,
  onClick,
}) => {
  const node = useRef(null)

  let count = 0

  /* eslint-disable-next-line default-case */
  switch (barrierType) {
    case 'dams': {
      count = dams
      break
    }
    case 'small_barriers': {
      count = smallBarriers
      break
    }

    // TODO: combined
  }

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

        {showCount && !disabled ? (
          <Text
            sx={{ fontSize: '0.9rem', color: 'grey.6', fontWeight: 'normal' }}
          >
            ({formatNumber(count)} {barrierTypeLabels[barrierType]}
            {count === 0 ? ', not available for prioritization' : ''})
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
  barrierType: PropTypes.string.isRequired,
  id: PropTypes.string.isRequired,
  name: PropTypes.string.isRequired,
  onClick: PropTypes.func.isRequired,
  state: PropTypes.string,
  layer: PropTypes.string,
  ranked_dams: PropTypes.number,
  ranked_small_barriers: PropTypes.number,
  crossings: PropTypes.number,
  showID: PropTypes.bool,
  showCount: PropTypes.bool,
  disabled: PropTypes.bool,
  focused: PropTypes.bool,
}

ListItem.defaultProps = {
  state: '',
  layer: '',
  ranked_dams: 0,
  ranked_small_barriers: 0,
  crossings: 0,
  showID: false,
  showCount: false,
  disabled: false,
  focused: false,
}

export default memo(ListItem)
