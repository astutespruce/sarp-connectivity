import { Text as BaseText } from 'rebass/styled-components'
import { display, fontSize, margin } from 'styled-system'

import styled, { themeGet } from 'style'

import ExpandableParagraph from './ExpandableParagraph'

// annotate Text so that it can be shown or hidden based on viewport size
// WARNING: we had to mix in props previously available from rebass: fontSize, margin
// watch for others that are no longer supported
const Text = styled(BaseText)`
  ${display}
  ${fontSize}
  ${margin}
`

const HelpText = styled(Text)`
  line-height: 1.4;
  color: ${themeGet('colors.grey.700')};
`

export { Text, HelpText, ExpandableParagraph }
