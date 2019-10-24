import React from 'react'
import { createPortal } from 'react-dom'
import PropTypes from 'prop-types'
import { Box, Flex } from 'components/Grid'
import { Text } from 'components/Text'
import styled, { themeGet } from 'style'

const Wrapper = styled(Flex).attrs({
  alignItems: 'center',
  justifyContent: 'center',
})`
  position: absolute;
  top: 0;
  bottom: 0;
  left: 0;
  right: 0;
  z-index: 10000;
  overflow: auto;
`

const Background = styled.div`
  background-color: rgba(0, 0, 0, 0.5);
  position: absolute;
  z-index: 1;
  top: 0;
  bottom: 0;
  left: 0;
  right: 0;
`

const Header = styled(Box).attrs({ pb: '0.5rem', mb: '0.5rem' })`
  border-bottom: 0.25rem solid ${themeGet('colors.primary.800')};
`

const Title = styled(Text).attrs({ as: 'h3', fontSize: '1.75rem', m: 0 })``

const Container = styled(Box).attrs({ p: '2rem' })`
  background: #fff;
  z-index: 2;
  border-radius: 1rem;
  box-shadow: 1px 1px 6px #000;
`

const index = ({ children, title, onClose }) => {
  const handleClose = () => {
    onClose()
  }

  return createPortal(
    <Wrapper>
      <Background onClick={handleClose} />
      <Container>
        <Header>
          <Title>{title}</Title>
        </Header>

        {children}
      </Container>
    </Wrapper>,
    document.body
  )
}

index.propTypes = {
  title: PropTypes.string.isRequired,
  children: PropTypes.node.isRequired,
  onClose: PropTypes.func.isRequired,
}

export default index
