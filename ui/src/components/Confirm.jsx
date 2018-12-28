import React from "react"
import PropTypes from "prop-types"

const Confirm = ({ active, children, onConfirm, onClose }) => (
    <div className={`modal ${active ? "is-active" : ""}`}>
        <div className="modal-background" onClick={onClose} />
        <div className="modal-content" style={{ width: 300 }}>
            <div className="box">
                {children}
                <div className="flex-container flex-justify-space-between" style={{ marginTop: "2rem" }}>
                    <button type="button" className="button" onClick={onClose}>
                        No
                    </button>
                    <button type="button" className="button is-danger" onClick={onConfirm}>
                        Yes
                    </button>
                </div>
            </div>
        </div>
        <button type="button" className="modal-close is-large" aria-label="close" onClick={onClose} />
    </div>
)

Confirm.propTypes = {
    active: PropTypes.bool,
    children: PropTypes.node.isRequired,
    onConfirm: PropTypes.func.isRequired,
    onClose: PropTypes.func.isRequired
}

Confirm.defaultProps = {
    active: false
}

export default Confirm
