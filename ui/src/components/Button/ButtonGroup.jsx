import { Flex } from 'components/Grid'
import styled from 'style'

const ButtonGroup = styled(Flex).attrs({ alignItems: 'center' })`
  button + button {
    border-left: 1px solid #fff;
  }

  button:first-child {
    border-radius: 6px 0 0 6px;
  }

  button:last-child {
    border-radius: 0 6px 6px 0;
  }

  button:not(:first-child):not(:last-child) {
    border-radius: 0;
  }
`

export default ButtonGroup
