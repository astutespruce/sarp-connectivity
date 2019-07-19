import { FaTimesCircle } from 'react-icons/fa'

import styled, {themeGet} from 'style'

const CloseButton = styled(FaTimesCircle)`
flex: 0 0 auto;
  width: 1.25rem;
  height: 1.25rem;
  cursor: pointer;
  color: ${themeGet('colors.grey.500')};

  &:hover {
    color: ${themeGet('colors.grey.900')};
  }
`

export default CloseButton