import { Flex, Box } from 'reflexbox/styled-components'
import { display } from 'styled-system'

import styled from 'style'

export const Columns = styled(Flex).attrs({
  flexWrap: ['wrap', 'nowrap'],
  justifyContent: 'space-between',
  mx: '-1rem',
  width: 'calc(100% + 2rem)',
})``

export const Column = styled(Box).attrs({
  flex: '1 1 auto',
  px: '1rem',
  mt: ['1rem', '1rem', 0],
})`
  ${display}
`

export const RightColumn = styled(Column)`
  text-align: right;
`
