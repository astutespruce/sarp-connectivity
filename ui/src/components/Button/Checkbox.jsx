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

// import React from 'react'
// import PropTypes from 'prop-types'

// import styled, { themeGet } from 'style'

// const HTMLCheckbox = styled.input.attrs({ type: 'checkbox' })`
//   display: none;
// `

// const Label = styled.label`
//   font-weight: bold;
//   font-size: 1.2em;
//   position: relative;
//   padding-left: 32px;
//   display: block;

//   /* box */
//   &::before {
//     content: '';
//     position: absolute;
//     left: 0;
//     display: inline-block;
//     height: 24px;
//     width: 24px;
//     border: 1px solid ${themeGet('colors.grey.700')};
//     border-radius: 0.25em;
//     cursor: pointer;
//     background-color: #fff;
//     transition: background-color 250ms ease-in;

//     ${HTMLCheckbox}:focus + &,
//     ${HTMLCheckbox}:hover + &,
//     ${HTMLCheckbox}:checked + & {
//       border-color: ${themeGet('colors.primary.500')};
//     }

//     ${HTMLCheckbox}:checked + & {
//       background-color: ${themeGet('colors.primary.500')};
//     }
//   }

//   /* checkmark */
//   &::after {
//     content: none;
//     position: absolute;
//     left: 4px;
//     top: 5px;
//     display: inline-block;
//     height: 0.5rem;
//     width: 1rem;

//     border-left: 4px solid #fff;
//     border-bottom: 4px solid #fff;
//     transform: rotate(-50deg);
//     cursor: pointer;

//     ${HTMLCheckbox}:checked + & {
//       content: '';
//     }
//   }
// `

// const Checkbox = ({ id, checked, label, onChange, ...props }) => {
//   const handleChange = ({ target: { checked: isChecked } }) => {
//     onChange(isChecked)
//   }
//   return (
//     <div {...props}>
//       <HTMLCheckbox id={id} checked={checked} onChange={handleChange} />
//       <Label htmlFor={id}>{label}</Label>
//     </div>
//   )
// }

// Checkbox.propTypes = {
//   // needed to hook the label to the hidden HTML checkbox
//   id: PropTypes.string.isRequired,
//   checked: PropTypes.bool,
//   label: PropTypes.string,
//   onChange: PropTypes.func.isRequired,
// }

// Checkbox.defaultProps = {
//   checked: false,
//   label: '',
// }

// export default Checkbox
