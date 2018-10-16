import PropTypes from "prop-types"

export const LabelPointPropType = PropTypes.shape({
    point: PropTypes.arrayOf(PropTypes.number.isRequired).isRequired,
    label: PropTypes.oneOfType([PropTypes.number, PropTypes.string])
})

export default { LabelPointPropType }
