import React from 'react'
import PropTypes from 'prop-types'
import { Button, Flex, Text } from 'theme-ui'
import { AngleDoubleRight } from '@emotion-icons/fa-solid'

const SubmitButton = ({ label, disabled, title, onClick }) => (
  <Button
    onClick={onClick}
    disabled={disabled}
    variant={disabled ? 'disabled' : 'primary'}
    title={title}
  >
    <Flex sx={{ alignItems: 'center', gap: '0.5rem' }}>
      <AngleDoubleRight size="1.2em" />
      <Text>{label}</Text>
    </Flex>
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
  disabled: null,
}

export default SubmitButton
