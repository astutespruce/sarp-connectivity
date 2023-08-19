/* eslint-disable default-case */
import React, { useState, useRef } from 'react'
import PropTypes from 'prop-types'
import {
  arrow,
  flip,
  shift,
  autoUpdate,
  useFloating,
  useInteractions,
  useHover,
  useFocus,
  useRole,
  useDismiss,
  FloatingPortal,
} from '@floating-ui/react-dom-interactions'
import { Box } from 'theme-ui'

const arrowBaseCSS = {
  position: 'absolute',
  zIndex: 1,
  width: '0.75rem',
  height: '0.75rem',
  bg: 'grey.9',
  transform: 'rotate(45deg)',
}

const Tooltip = ({ children, content, direction, maxWidth, fontSize }) => {
  const [open, setOpen] = useState(false)
  const arrowRef = useRef(null)
  const {
    context,
    x,
    y,
    reference,
    floating,
    strategy,
    placement,
    middlewareData: {
      arrow: { x: arrowX, y: arrowY } = {},
      shift: { x: shiftX, y: shiftY } = {},
    },
  } = useFloating({
    strategy: 'absolute',
    placement: direction,
    open,
    onOpenChange: setOpen,
    whileElementsMounted: autoUpdate,
    middleware: [arrow({ element: arrowRef }), flip(), shift()],
  })
  const { getReferenceProps, getFloatingProps } = useInteractions([
    useHover(context),
    useFocus(context),
    useRole(context, { role: 'tooltip' }),
    useDismiss(context),
  ])

  let arrowCSS = null

  switch (placement) {
    case 'top': {
      arrowCSS = {
        ...arrowBaseCSS,
        bottom: '0.375rem',
        left: `${arrowX - (shiftX || 0)}px`,
      }
      break
    }
    case 'bottom': {
      arrowCSS = {
        ...arrowBaseCSS,
        top: '0.375rem',
        left: `${arrowX - (shiftX || 0)}px`,
      }
      break
    }
    case 'left': {
      arrowCSS = {
        ...arrowBaseCSS,
        right: '0.375rem',
        top: `${arrowY - (shiftY || 0)}px`,
      }
      break
    }
    case 'right': {
      arrowCSS = {
        ...arrowBaseCSS,
        left: '0.375rem',
        top: `${arrowY - (shiftY || 0)}px`,
      }
      break
    }
  }

  return (
    <>
      <span ref={reference} {...getReferenceProps()}>
        {children}
      </span>
      <FloatingPortal>
        {open && (
          <Box
            ref={floating}
            {...getFloatingProps()}
            sx={{
              position: strategy,
              top: y ?? 0,
              left: x ?? 0,
              p: '0.75rem',
              zIndex: 10000,
            }}
          >
            <Box
              sx={{
                position: 'relative',
                zIndex: 2,
                bg: '#FFF',
                p: '0.5em',
                borderRadius: '0.5em',
                boxShadow: '1px 1px 3px #333',
                border: '1px solid',
                borderColor: 'grey.3',
                overflow: 'hidden',
                maxWidth,
                fontSize,
              }}
            >
              {content}
            </Box>
            <Box ref={arrowRef} sx={arrowCSS} />
          </Box>
        )}
      </FloatingPortal>
    </>
  )
}

Tooltip.propTypes = {
  children: PropTypes.oneOfType([PropTypes.string, PropTypes.node]).isRequired,
  content: PropTypes.oneOfType([PropTypes.string, PropTypes.node]).isRequired,
  direction: PropTypes.string,
  maxWidth: PropTypes.string,
  fontSize: PropTypes.oneOfType([PropTypes.number, PropTypes.string]),
}

Tooltip.defaultProps = {
  direction: 'right',
  maxWidth: '28rem',
  fontSize: 1,
}

export default Tooltip
