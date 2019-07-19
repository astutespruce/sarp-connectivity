import React from 'react'
import { FaSync } from 'react-icons/fa'

import { Flex } from 'components/Grid'
import styled, { keyframes, themeGet } from 'style'

const Wrapper = styled(Flex).attrs({
  alignItems: 'center',
  justifyContent: 'center',
})`
  flex: 1 1 auto;
  height: 100%;
`

const rotate = keyframes`
  from {
    transform: rotate(0deg);
  }

  to {
    transform: rotate(360deg);
  }
`

const Spinner = styled(FaSync)`
  height: 2rem;
  width: 2rem;
  animation: ${rotate} 2s linear infinite;
  color: ${themeGet('colors.primary.500')};
  margin-right: 1em;
`

const Label = styled.div`
  font-size: 2rem;
  color: ${themeGet('colors.grey.700')};
`

const LoadingSpinner = () => {
  return (
    <Wrapper>
      <Spinner />
      <Label>Loading...</Label>
    </Wrapper>
  )
}

export default LoadingSpinner
