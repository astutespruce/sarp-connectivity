import React from 'react'
import PropTypes from 'prop-types'

import { Text } from 'components/Text'
import { Icon } from 'components/Icon'
import { Box, Flex } from 'components/Grid'
import styled, { themeGet } from 'style'

const Wrapper = styled(Box).attrs({ p: '1rem' })`
  background: ${themeGet('colors.primary.100')};
  border-radius: 0.5rem;
`

const Header = styled(Flex).attrs({ alignItems: 'center' })`
  margin-bottom: 0.5rem;
  padding-bottom: 0.5rem;
  border-bottom: 4px solid #fff;
`

const Title = styled(Text).attrs({ as: 'h3', fontSize: '2rem' })`
  flex: 1;
  margin: 0 0 0 0.25rem;
  font-weight: normal;
`

const Content = styled(Text)`
  line-height: 1.5;
  color: ${themeGet('colors.primary.900')};
`

const HighlightBox = ({ icon, title, children }) => {
  return (
    <Wrapper>
      <Header>
        {icon ? <Icon name={icon} size="3rem" /> : null}
        <Title>{title}</Title>
      </Header>
      <Content>{children}</Content>
    </Wrapper>
  )
}

HighlightBox.propTypes = {
  icon: PropTypes.string,
  title: PropTypes.string.isRequired,
  children: PropTypes.node.isRequired,
}

HighlightBox.defaultProps = {
  icon: null,
}

export default HighlightBox
