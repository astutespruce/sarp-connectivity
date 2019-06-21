import { Box, Container, Column as BaseColumn } from 'components/Grid'

import { Text } from 'components/Text'
import styled, { themeGet } from 'style'

export const PageContainer = styled(Container).attrs({
  px: ['1rem', '1rem', 0],
  mt: '2rem',
  mb: '4rem',
})``

export const PageTitle = styled(Text).attrs({ as: 'h1', fontSize: '3rem' })``

export const Section = styled(Box)`
  color: ${themeGet('colors.grey.900')};

  &:not(:first-child) {
    margin-top: 3rem;
  }

  p {
    font-size: 1.1rem;
    margin: 0;
  }

  ul,
  ol {
    margin-bottom: 0;
    line-height: 1.2;
  }

  ol li {
    margin: 0;

    & + li {
      margin-top: 0.5rem;
    }
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

export const Subtitle = styled(Text)``

export const Column = styled(BaseColumn).attrs({
  width: ['100%', '100%', '50%'],
})`
  display: flex;
  flex-direction: column;
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

export const LargeText = styled(Text).attrs({ as: 'p' })`
  margin-top: 2rem;
  font-size: 1.5rem;
`
