import React from "react"
import PropTypes from "prop-types"

const SubmitButton = ({ label, icon, disabled, onClick }) => (
    <button className="button is-medium is-info" type="button" onClick={onClick} disabled={disabled}>
        {icon !== null && <i className={`fa fa-${icon}`} style={{ marginRight: "0.25em" }} />}
        {label}
    </button>
)

SubmitButton.propTypes = {
    label: PropTypes.string.isRequired,
    icon: PropTypes.string,
    disabled: PropTypes.bool,
    onClick: PropTypes.func.isRequired
}

SubmitButton.defaultProps = {
    disabled: false,
    icon: null
}

export default SubmitButton
