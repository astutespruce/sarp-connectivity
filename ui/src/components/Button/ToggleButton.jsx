import React, { memo } from 'react'
import PropTypes from 'prop-types'
import { Button } from 'theme-ui'

import ButtonGroup from './ButtonGroup'

const ToggleButton = ({ value, options, onChange, ...props }) => {
  const handleClick = (newValue) => {
    if (newValue === value) return

    onChange(newValue)
  }

  if (value === null)
    return (
      <ButtonGroup {...props}>
        {options.map(({ value: v, label }) => (
          <Button
            key={v}
            onClick={() => handleClick(v)}
            variant="toggle-inactive"
          >
            {label}
          </Button>
        ))}
      </ButtonGroup>
    )

  return (
    <ButtonGroup {...props}>
      {options.map(({ value: v, label }) =>
        v === value ? (
          <Button key={v} variant="toggle-active">
            {label}
          </Button>
        ) : (
          <Button
            key={v}
            onClick={() => handleClick(v)}
            variant="toggle-inactive"
          >
            {label}
          </Button>
        )
      )}
    </ButtonGroup>
  )
}

ToggleButton.propTypes = {
  value: PropTypes.oneOfType([PropTypes.string, PropTypes.number]),
  options: PropTypes.arrayOf(
    PropTypes.shape({
      value: PropTypes.oneOfType([PropTypes.string, PropTypes.number])
        .isRequired,
      label: PropTypes.string.isRequired,
    })
  ).isRequired,
  onChange: PropTypes.func.isRequired,
}

ToggleButton.defaultProps = {
  value: null,
}

export default memo(
  ToggleButton,
  ({ value: prevValue }, { value: nextValue }) => prevValue === nextValue
)
