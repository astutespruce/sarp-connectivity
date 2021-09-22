import React, { useCallback, useState } from 'react'
import PropTypes from 'prop-types'
import { usePopper } from 'react-popper'
import { Box } from 'theme-ui'

const arrowBaseCSS = {
  content: '""',
  boxSizing: 'border-box',
  position: 'absolute',
  border: '4px solid transparent',
  height: '2px',
  width: '2px',
}

const leftArrowCSS = {
  width: '4px',
  height: '4px',
  left: '-4px',
  '::after': {
    ...arrowBaseCSS,
    top: '-4px',
    borderBottomColor: 'grey.9',
    borderLeftColor: 'grey.9',
    transform: 'rotate(45deg)',
  },
}

const rightArrowCSS = {
  width: '4px',
  height: '4px',
  right: '4px',
  '::after': {
    ...arrowBaseCSS,
    top: '-4px',
    borderRightColor: 'grey.9',
    borderTopColor: 'grey.9',
    transform: 'rotate(45deg)',
  },
}

const bottomArrowCSS = {
  width: '4px',
  height: '4px',
  top: 'unset',
  bottom: '0',
  '::after': {
    ...arrowBaseCSS,
    borderRightColor: 'grey.9',
    borderTopColor: 'grey.9',
    transform: 'rotate(135deg)',
  },
}

const topArrowCSS = {
  width: '4px',
  height: '4px',
  top: 0,
  left: 'unset',
  '::after': {
    ...arrowBaseCSS,
    top: '-4px',
    borderRightColor: 'grey.9',
    borderTopColor: 'grey.9',
    transform: 'rotate(-45deg)',
  },
}

const arrowCSS = {
  '&[data-popper-placement="right"] [data-popper-rel="arrow"]': leftArrowCSS,
  '&[data-popper-placement="left"] [data-popper-rel="arrow"]': rightArrowCSS,
  '&[data-popper-placement="top"] [data-popper-rel="arrow"]': bottomArrowCSS,
  '&[data-popper-placement="bottom"] [data-popper-rel="arrow"]': topArrowCSS,
}

const Tooltip = ({
  direction,
  altDirections,
  content,
  children,
  inline,
  sx,
}) => {
  // Have to use callback ref instead of regular useRef
  const [arrowNode, setArrowNode] = useState(null)
  const [anchorNode, setAnchorNode] = useState(null)
  const [tooltipNode, setTooltipNode] = useState(null)
  const [isVisible, setIsVisible] = useState(false)

  const handleMouseEnter = useCallback(() => {
    setIsVisible(() => true)
  }, [])

  const handleMouseLeave = useCallback(() => {
    setIsVisible(() => false)
  }, [])

  const { styles, attributes } = usePopper(anchorNode, tooltipNode, {
    placement: direction,
    strategy: 'absolute',
    modifiers: [
      {
        name: 'arrow',
        options: {
          element: arrowNode,
        },
      },
      {
        name: 'offset',
        options: {
          offset: [0, 8],
        },
      },
      {
        name: 'flip',
        options: {
          fallbackPlacements: altDirections || [],
        },
      },
    ],
  })

  return (
    <>
      <Box
        ref={setAnchorNode}
        onMouseEnter={handleMouseEnter}
        onMouseLeave={handleMouseLeave}
        sx={{
          display: inline ? 'inline-block' : 'block',
        }}
      >
        {children}
      </Box>

      <Box
        ref={setTooltipNode}
        style={{ ...styles.popper, zIndex: 10000 }}
        sx={arrowCSS}
        {...attributes.popper}
      >
        {isVisible && (
          <>
            <Box
              ref={setArrowNode}
              style={styles.arrow}
              data-popper-rel="arrow"
            />
            <Box
              style={styles.offset}
              sx={{
                bg: '#FFF',
                p: '0.5em',
                borderRadius: '0.5em',
                boxShadow: '1px 1px 3px #999',
                border: '1px solid',
                borderColor: 'grey.3',
                overflow: 'hidden',
              }}
            >
              <Box sx={sx}>{content}</Box>
            </Box>
          </>
        )}
      </Box>
    </>
  )
}

Tooltip.propTypes = {
  direction: PropTypes.string,
  altDirections: PropTypes.arrayOf(PropTypes.string),
  title: PropTypes.string,
  content: PropTypes.node.isRequired,
  children: PropTypes.node.isRequired,
  sx: PropTypes.object,
  inline: PropTypes.bool,
}

Tooltip.defaultProps = {
  direction: 'auto',
  altDirections: [],
  title: null,
  sx: null,
  inline: false,
}

export default Tooltip
