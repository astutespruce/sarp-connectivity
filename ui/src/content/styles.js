import { Box, Container, Column as BaseColumn, Flex } from 'components/Grid'

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

  &:not(:first-of-type) {
    margin-top: 6rem;
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

export const StepHeader = styled(Flex).attrs({ alignItems: 'center' })`
  font-size: 1.5rem;
  line-height: 1.2;
  margin-bottom: 1rem;
`

// Flex so that we can position content vertically aligned
export const StepNumber = styled(Flex)`
  color: #fff;
  background-color: ${themeGet('colors.grey.900')};
  border-radius: 5em;
  width: 2em;
  height: 2em;
  align-items: center;
  justify-content: center;
  font-weight: bold;
  margin-right: 0.5rem;
  flex: 0 0 auto;
`

export const Divider = styled.div`
  height: 0.5rem;
  background-color: ${themeGet('colors.primary.800')};
  margin-bottom: 2rem;
`
