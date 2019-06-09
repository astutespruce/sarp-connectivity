import { Box } from 'components/Grid'

import { Text } from 'components/Text'
import styled, { themeGet } from 'style'

export const Section = styled(Box)`
  &:not(:first-child) {
    margin-top: 3rem;
  }

  p {
    font-size: 1.1rem;
    color: ${themeGet('colors.grey.800')};
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
