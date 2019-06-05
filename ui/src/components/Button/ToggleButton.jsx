import React, { memo } from 'react'
import PropTypes from 'prop-types'

import styled from 'style'
import { DefaultButton, PrimaryButton } from './Button'
import ButtonGroup from './ButtonGroup'

const ToggleButton = ({ value, options, onChange, ...props }) => {
  const handleClick = newValue => {
    if (newValue === value) return

    onChange(newValue)
  }

  if (value === null)
    return (
      <ButtonGroup {...props}>
        {options.map(({ value: v, label }) => (
          <PrimaryButton key={v} onClick={() => handleClick(v)}>
            {label}
          </PrimaryButton>
        ))}
      </ButtonGroup>
    )

  return (
    <ButtonGroup {...props}>
      {options.map(({ value: v, label }) =>
        v === value ? (
          <PrimaryButton key={v}>{label}</PrimaryButton>
        ) : (
          <DefaultButton key={v} onClick={() => handleClick(v)}>
            {label}
          </DefaultButton>
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
