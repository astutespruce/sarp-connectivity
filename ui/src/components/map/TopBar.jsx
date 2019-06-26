import { Flex } from 'components/Grid'
import styled from 'style'

const TopBar = styled(Flex).attrs({ alignItems: 'center', p: '0.5rem' })`
  position: absolute;
  top: 0;
  left: 10px;
  z-index: 1000;
  background: #fff;
  border-radius: 0 0 0.25rem 0.25rem;
  box-shadow: 1px 1px 8px #333;
`

export default TopBar
