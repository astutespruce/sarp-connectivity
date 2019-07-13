import React from 'react'
import PropTypes from 'prop-types'

import { Box, Flex } from 'components/Grid'
import { Text } from 'components/Text'
import { PrimaryButton, WarningButton } from 'components/Button'
import styled, { themeGet } from 'style'

const Wrapper = styled(Flex).attrs({
  justifyContent: 'center',
  alignItems: 'center',
})`
  position: absolute;
  z-index: 100000;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
`

const Background = styled.div`
  position: absolute;
  z-index: 1;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(10, 10, 10, 0.86);
  cursor: pointer;
`

const Content = styled(Box).attrs({ p: '1.25rem' })`
  z-index: 2;
  margin: 0 auto;
  width: 300px;
  position: relative;
  border-radius: 0.5rem;
  background: #fff;
`

const Title = styled(Text).attrs({ as: 'h4', fontSize: '1.25rem' })``

const ButtonContainer = styled(Flex).attrs({ justifyContent: 'space-between' })`
  padding-top: 1rem;
  margin-top: 2rem;
  border-top: 1px solid ${themeGet('colors.grey.200')};
`

const Confirm = ({ title, children, onConfirm, onClose }) => (
  <Wrapper>
    <Background onClick={onClose} />
    <Content>
      <Title>{title}</Title>

      {children}

      <ButtonContainer>
        <PrimaryButton onClick={onClose}>No</PrimaryButton>
        <WarningButton onClick={onConfirm}>Yes</WarningButton>
      </ButtonContainer>
    </Content>
  </Wrapper>
)

Confirm.propTypes = {
  title: PropTypes.string.isRequired,
  children: PropTypes.node.isRequired,
  onConfirm: PropTypes.func.isRequired,
  onClose: PropTypes.func.isRequired,
}

export default Confirm
