import React, { memo } from 'react'
import PropTypes from 'prop-types'

import styled, { themeGet } from 'style'

export const InactiveButton = styled.div`
  text-align: center;
  cursor: pointer;
  flex-grow: 1;
  padding: 0.25rem 0.5rem;
  color: ${themeGet('colors.grey.700')};
  border-bottom: 1px solid ${themeGet('colors.grey.300')};
  &:hover {
    background-color: ${themeGet('colors.grey.200')};
  }
`

export const ActiveButton = styled(InactiveButton)`
  font-weight: bold;
  color: ${themeGet('colors.grey.900')};
  border-bottom-color: transparent;
  background-color: #fff !important;
  &:not(:first-of-type) {
    border-left: 1px solid ${themeGet('colors.grey.300')};
  }
  &:not(:last-of-type) {
    border-right: 1px solid ${themeGet('colors.grey.300')};
  }
`

const Button = ({ id, label, active, onClick }) => {
  const handleClick = () => {
    onClick(id)
  }
  return active ? (
    <ActiveButton>{label}</ActiveButton>
  ) : (
    <InactiveButton onClick={handleClick}>{label}</InactiveButton>
  )
}

Button.propTypes = {
  id: PropTypes.string.isRequired,
  label: PropTypes.string.isRequired,
  active: PropTypes.bool,
  onClick: PropTypes.func.isRequired,
}

Button.defaultProps = {
  active: false,
}

export default memo(
  Button,
  ({ id: prevId, active: prevActive }, { id: nextId, active: nextActive }) =>
    prevId === nextId && prevActive === nextActive
)
