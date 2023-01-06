import React from 'react'
import PropTypes from 'prop-types'
import { SearchLocation } from '@emotion-icons/fa-solid'
import { Button } from 'theme-ui'

const SubmitButton = ({ label, disabled, title, onClick }) => (
  <Button
    onClick={onClick}
    disabled={disabled}
    variant={disabled ? 'disabled' : 'primary'}
    title={title}
  >
    <SearchLocation size="1.2em" style={{ marginRight: '0.25em' }} />
    {label}
  </Button>
)

SubmitButton.propTypes = {
  label: PropTypes.string.isRequired,
  disabled: PropTypes.bool,
  title: PropTypes.string,
  onClick: PropTypes.func.isRequired,
}

SubmitButton.defaultProps = {
  title: null,
}

SubmitButton.defaultProps = {
  disabled: false,
}

export default SubmitButton
