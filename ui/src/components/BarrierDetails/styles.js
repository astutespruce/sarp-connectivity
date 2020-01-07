import { Text, HelpText } from 'components/Text'
import styled, { themeGet } from 'style'

export const Section = styled.div`
  &:not(:first-child) {
    margin-top: 0.5rem;
    padding-top: 0.5rem;
    border-top: 1px solid ${themeGet('colors.grey.200')};
  }
`

export const SectionHeader = styled(Text).attrs({
  as: 'h4',
  fontSize: '1rem',
  mb: '0.5rem',
})``

export const List = styled.ul`
  list-style: disc;
  margin-top: 0;
  li {
    margin-bottom: 0;
  }
  li:not(:first-child) {
    margin-top: 0.5rem;
  }
`

export const Note = styled(HelpText).attrs({
  mt: '1rem',
  fontSize: 'smaller',
})``

export const SecondaryText = styled(HelpText).attrs({
  fontSize: 'smaller',
})``
