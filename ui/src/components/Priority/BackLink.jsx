import React from 'react'
import PropTypes from 'prop-types'
import { Reply } from '@emotion-icons/fa-solid'
import { Button } from 'theme-ui'

const BackLink = ({ label, onClick }) => (
  <Button
    onClick={onClick}
    sx={{
      outline: 'none',
      border: 'none',
      background: 'none',
      color: 'link',
      display: 'block',
      p: 0,
      fontSize: '1rem',
      m: '-0.75rem 0 0.5rem -0.75rem',
    }}
  >
    <Reply size="1.1rem" style={{ marginRight: '0.25rem' }} /> {label}
  </Button>
)

BackLink.propTypes = {
  label: PropTypes.string.isRequired,
  onClick: PropTypes.func.isRequired,
}

export default BackLink
