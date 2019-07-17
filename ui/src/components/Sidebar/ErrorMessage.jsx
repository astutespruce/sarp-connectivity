import React from 'react'
import PropTypes from 'prop-types'
import { FaExclamationTriangle } from 'react-icons/fa'

import { Flex } from 'components/Grid'
import styled, { themeGet } from 'style'

const Wrapper = styled(Flex).attrs({
  alignItems: 'center',
  justifyContent: 'center',
  flexDirection: 'column',
  p: '1rem',
})`
  flex: 1 1 auto;
  height: 100%;
`

export const WarningIcon = styled(FaExclamationTriangle)`
  height: 2em;
  width: 2em;
  margin-right: 0.5em;
  color: ${themeGet('colors.highlight.500')};
`

export const Label = styled.div`
  color: ${themeGet('colors.highlight.500')};
  font-size: 2rem;
`

const Error = ({ children }) => {
  return (
    <Wrapper>
      <Flex alignItems="center" mb="1rem">
        <WarningIcon />
        <Label>Whoops!</Label>
      </Flex>
      {children}
    </Wrapper>
  )
}

Error.propTypes = {
  children: PropTypes.node.isRequired,
}

export default Error
