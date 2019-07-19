import PropTypes from 'prop-types'

export const GraphQLArrayPropType = node =>
  PropTypes.shape({
    edges: PropTypes.arrayOf(
      PropTypes.shape({
        node,
      })
    ),
  })

export const extractNodes = ({ edges }) => edges.map(({ node }) => node)
