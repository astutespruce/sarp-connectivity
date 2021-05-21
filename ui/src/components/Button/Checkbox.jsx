import React from 'react'
import PropTypes from 'prop-types'
import { Checkbox as BaseCheckbox, Flex, Label } from 'theme-ui'

const Checkbox = ({ checked, label, onChange, ...props }) => (
  <Flex {...props}>
    <Label
      sx={{
        lineHeight: 1.5,
        width: 'auto',
        'input:focus~svg': {
          color: 'grey.8',
          backgroundColor: 'transparent !important',
        },
        'input:checked~svg': {
          color: 'grey.8',
        },
      }}
    >
      <BaseCheckbox
        readOnly={false}
        checked={checked}
        onChange={onChange}
        sx={{
          cursor: 'pointer',
          mr: '0.1em',
          width: '1.5em',
          height: '1.5em',
        }}
      />
      {label}
    </Label>
  </Flex>
)

Checkbox.propTypes = {
  checked: PropTypes.bool,
  label: PropTypes.oneOfType([PropTypes.string, PropTypes.node]).isRequired,
  onChange: PropTypes.func.isRequired,
}

Checkbox.defaultProps = {
  checked: false,
}

export default Checkbox
