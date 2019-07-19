import React from 'react'
import PropTypes from 'prop-types'
import { FaReply } from 'react-icons/fa'

import styled, { themeGet } from 'style'

const BackIcon = styled(FaReply)`
  height: 1em;
  width: 1em;
  margin-right: 0.25em;
`

const Link = styled.button.attrs({ type: 'button' })`
  outline: none;
  border: none;
  background: none;
  color: ${themeGet('colors.link')};
  display: block;
  padding: 0;
  font-size: 0.9rem;
  margin: -0.75rem 0 0.5rem -0.75rem;
`

const BackLink = ({ label, onClick }) => (
  <Link onClick={onClick}>
    <BackIcon /> {label}
  </Link>
)

BackLink.propTypes = {
  label: PropTypes.string.isRequired,
  onClick: PropTypes.func.isRequired,
}

export default BackLink
