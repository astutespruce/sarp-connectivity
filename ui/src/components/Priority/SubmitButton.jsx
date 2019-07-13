import React from 'react'
import PropTypes from 'prop-types'
import { FaSearchLocation } from 'react-icons/fa'

import { PrimaryButton } from 'components/Button'
import styled from 'style'

const Button = styled(PrimaryButton)`
  font-size: 1.1em;
  display: flex;
  align-items: center;
`

export const SearchIcon = styled(FaSearchLocation)`
  height: 1.2em;
  width: 1.2em;
  margin-right: 0.25em;
`

const SubmitButton = ({ label, disabled, onClick }) => (
  <Button onClick={onClick} disabled={disabled}>
    <SearchIcon />
    {label}
  </Button>
)

SubmitButton.propTypes = {
  label: PropTypes.string.isRequired,
  disabled: PropTypes.bool,
  onClick: PropTypes.func.isRequired,
}

SubmitButton.defaultProps = {
  disabled: false,
}

export default SubmitButton
