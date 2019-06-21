import {height, width} from 'styled-system'
import Image from 'gatsby-image'

import styled from 'style'

export { default as HeaderImage } from './HeaderImage'
export { default as Credits } from './Credits'
export {default as DividerImage} from './DividerImage'

export const GatsbyImage = styled(Image)`
${height}
${width}
`