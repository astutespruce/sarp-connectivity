import PropTypes from "prop-types"

// At minimum, a feature must have an id
export const FeaturePropType = PropTypes.shape({
    id: PropTypes.oneOfType([PropTypes.string, PropTypes.number]).isRequired
})

export const LabelPointPropType = PropTypes.shape({
    point: PropTypes.arrayOf(PropTypes.number.isRequired).isRequired,
    label: PropTypes.oneOfType([PropTypes.number, PropTypes.string])
})

export default { LabelPointPropType }
