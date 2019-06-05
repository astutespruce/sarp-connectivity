import PropTypes from 'prop-types'
import styled from 'style'
import { Box } from '@rebass/grid'

const Container = styled(Box).attrs({ px: '1rem' })`
  max-width: ${props => props.maxWidth};
`

Container.propTypes = {
  maxWidth: PropTypes.oneOfType([
    PropTypes.number,
    PropTypes.string,
    PropTypes.array,
  ]),
}

Container.defaultProps = {
  mx: 'auto',
  maxWidth: '1024px',
}

export default Container
