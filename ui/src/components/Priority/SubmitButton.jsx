import React from 'react'
import PropTypes from 'prop-types'
import { SearchLocation } from '@emotion-icons/fa-solid'
import { Button } from 'theme-ui'

const SubmitButton = ({ label, disabled, onClick }) => (
  <Button onClick={onClick} disabled={disabled}>
    <SearchLocation size="1.2em" style={{ marginRight: '0.25em' }} />
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
