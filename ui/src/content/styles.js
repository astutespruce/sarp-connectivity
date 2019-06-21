import { Box, Column } from 'components/Grid'

import { Text } from 'components/Text'
import styled, { themeGet } from 'style'

export const Section = styled(Box)`
  color: ${themeGet('colors.grey.900')};

  &:not(:first-child) {
    margin-top: 3rem;
  }

  p {
    font-size: 1.1rem;
    margin: 0;
  }

  ul {
    margin-bottom: 0;
  }
`

export const Title = styled(Text).attrs({
  fontSize: ['1.5rem', '2rem'],
  mb: '1.5rem',
  as: 'h2',
})`
  font-weight: bold;
  line-height: 1.2;
`

export const NarrowColumn = styled(Column).attrs({
  width: ['100%', '100%', '33%'],
  px: ['1rem', '1rem', 0],
})``

export const WideColumn = styled(Column).attrs({
  width: ['100%', '100%', '66%'],
})``

export const ImageCredits = styled(Box).attrs({})`
  color: ${themeGet('colors.grey.600')};
  font-size: 0.8rem;
  line-height: 1.2;
`