import React, { useState } from "react"
import PropTypes from "prop-types"
import { push } from "connected-react-router"
import { connect } from "react-redux"

import Confirm from "../../Confirm"

const StartOverButton = ({ redirect }) => {
    const [confirmIsActive, setConfirmIsActive] = useState(false)

    const handleConfirm = () => {
        setConfirmIsActive(false)
        redirect("/priority")
    }

    return (
        <React.Fragment>
            <Confirm active={confirmIsActive} onConfirm={handleConfirm} onClose={() => setConfirmIsActive(false)}>
                <h4 className="title is-4">Start Over?</h4>
                <p>You will lose all your work. Are you sure?</p>
            </Confirm>
            <button
                className="button is-danger is-medium"
                type="button"
                style={{ marginRight: "1rem" }}
                title="Start Over"
                onClick={() => setConfirmIsActive(true)}
            >
                <i className="fa fa-trash" />
            </button>
        </React.Fragment>
    )
}

StartOverButton.propTypes = {
    redirect: PropTypes.func.isRequired
}

export default connect(
    null,
    { redirect: push }
)(StartOverButton)
