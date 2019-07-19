import { Text } from 'components/Text'
import styled, { themeGet } from 'style'

export const Section = styled.div`
  &:not(:first-child) {
    margin-top: 1rem;
  }
`

export const SectionHeader = styled(Text).attrs({
  as: 'h4',
  fontSize: '1rem',
  mb: '0.5rem',
})``

export const List = styled.ul`
  /* color: ${themeGet('colors.grey.800')}; */
  list-style: disc;
  margin-top: 0;
  li {
    margin-bottom: 0;
  }
  li + li {
    margin-top: 0.25rem;
  }
`
