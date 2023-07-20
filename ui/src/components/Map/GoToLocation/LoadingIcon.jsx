/** @jsxRuntime classic */
/** @jsx jsx */

// eslint-disable-next-line no-unused-vars
import React from 'react'
import { Compass as Icon } from '@emotion-icons/fa-solid'
import { keyframes, css } from '@emotion/react'
import { jsx } from 'theme-ui'

const animation = keyframes`
from {
transform: rotate(0deg);
}

to {
    transform: rotate(360deg);
}
`

const animationCSS = css`
  transform-origin: '50% 50%';
  animation: ${animation} 1s ease-in-out infinite;
`

const LoadingIcon = ({ ...props }) => <Icon {...props} css={animationCSS} />

export default LoadingIcon
