import React from 'react'
import PropTypes from 'prop-types'

import styled, { themeGet } from 'style'

const HTMLCheckbox = styled.input.attrs({ type: 'checkbox' })`
  display: none;
`

const Label = styled.label`
  font-weight: bold;
  font-size: 1.2rem;
  position: relative;
  padding-left: 2rem;

  /* box */
  &::before {
    content: '';
    position: absolute;
    left: 0;
    display: inline-block;
    height: 1.5rem;
    width: 1.5rem;
    border: 1px solid ${themeGet('colors.grey.700')};
    border-radius: 0.25rem;
    cursor: pointer;
    background-color: #fff;
    transition: background-color 250ms ease-in;

    ${HTMLCheckbox}:focus + &,
    ${HTMLCheckbox}:hover + &,
    ${HTMLCheckbox}:checked + & {
      border-color: ${themeGet('colors.primary.500')};
    }

    ${HTMLCheckbox}:checked + & {
      background-color: ${themeGet('colors.primary.500')};
    }
  }

  /* checkmark */
  &::after {
    content: none;
    position: absolute;
    left: 4px;
    top: 5px;
    display: inline-block;
    height: 0.5rem;
    width: 1rem;

    border-left: 4px solid #fff;
    border-bottom: 4px solid #fff;
    transform: rotate(-50deg);
    cursor: pointer;

    ${HTMLCheckbox}:checked + & {
      content: '';
    }
  }
`

const Checkbox = ({ id, checked, label, onChange }) => {
  const handleChange = ({ target: { checked: isChecked } }) => {
    onChange(isChecked)
  }
  return (
    <>
      <HTMLCheckbox id={id} checked={checked} onChange={handleChange} />
      <Label htmlFor={id}>{label}</Label>
    </>
  )
}

Checkbox.propTypes = {
  // needed to hook the label to the hidden HTML checkbox
  id: PropTypes.string.isRequired,
  checked: PropTypes.bool,
  label: PropTypes.string,
  onChange: PropTypes.func.isRequired,
}

Checkbox.defaultProps = {
  checked: false,
  label: '',
}

export default Checkbox
