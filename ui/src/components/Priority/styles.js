import { FaExclamationTriangle } from 'react-icons/fa'

import { Text } from 'components/Text'
import { Box, Flex } from 'components/Grid'
import styled from 'style'

// sidebar wrapper
export const Wrapper = styled(Flex).attrs({ flexDirection: 'column' })`
  height: 100%;
`

export const Header = styled(Box).attrs({
  py: '1rem',
  pr: '0.5rem',
  pl: '1rem',
})`
  background: #f6f6f2;
  border-bottom: 1px solid #ddd;
  flex: 0 0 auto;
`

export const Footer = styled(Flex).attrs({
  justifyContent: 'space-between',
  alignItems: 'center',
  p: '1rem',
})`
  flex-grow: 0 0 auto;
  border-top: 1px solid #ddd;
  background: #f6f6f2;
`

export const Title = styled(Text).attrs({
  as: 'h3',
  mb: 0
})`
  font-size: 1.5rem;
  line-height: 1.2;
`

export const Content = styled(Box).attrs({ p: '1rem' })`
  overflow-y: auto;
  overflow-x: hidden;
  flex-grow: 1;
`

export const WarningIcon = styled(FaExclamationTriangle)`
  height: 1em;
  width: 1em;
  margin-right: 0.25em;
`
