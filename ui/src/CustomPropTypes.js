import PropTypes from "prop-types"
import ImmutablePropTypes from "react-immutable-proptypes"

// At minimum, a feature must have an id
export const FeaturePropType = ImmutablePropTypes.mapContains({
    id: PropTypes.oneOfType([PropTypes.string, PropTypes.number]).isRequired,
    layerId: PropTypes.string.isRequired
})

export const LabelPointPropType = PropTypes.shape({
    point: PropTypes.arrayOf(PropTypes.number.isRequired).isRequired,
    label: PropTypes.oneOfType([PropTypes.number, PropTypes.string])
})

export default { LabelPointPropType }
