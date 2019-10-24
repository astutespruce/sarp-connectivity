import PropTypes from 'prop-types'
import styled from 'style'
import { Box } from 'reflexbox/styled-components'

const Container = styled(Box)`
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
  maxWidth: '960px',
}

export default Container
