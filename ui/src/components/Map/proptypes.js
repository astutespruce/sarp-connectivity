import PropTypes from 'prop-types'

export const LocationPropType = PropTypes.shape({
  latitude: PropTypes.number,
  longitude: PropTypes.number,
  timestamp: PropTypes.number,
})

// At minimum, a feature must have an id
export const FeaturePropType = PropTypes.shape({
  id: PropTypes.oneOfType([PropTypes.string, PropTypes.number]),
})

export const SearchFeaturePropType = PropTypes.shape({
  id: PropTypes.string,
  layer: PropTypes.string,
  bbox: PropTypes.arrayOf(PropTypes.number),
  maxZoom: PropTypes.number,
})
