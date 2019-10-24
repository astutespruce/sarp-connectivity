import { Flex, Box as BaseBox } from 'reflexbox/styled-components'
import { display } from 'styled-system'

import styled from 'style'
import Container from './Container'
import { Columns, Column, RightColumn } from './Columns'

// Annotate box so that it can be shown or hidden based on viewport size
const Box = styled(BaseBox)`
  ${display}
`

export { Flex, Box, Container, Columns, Column, RightColumn }
