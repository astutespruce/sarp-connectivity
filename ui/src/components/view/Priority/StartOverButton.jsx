import React from "react"
import { Link } from "react-router-dom"

const StartOverButton = () => (
    <Link to="/priority">
        <button className="button is-black is-medium" type="button" style={{ marginRight: "1rem" }} title="Start Over">
            <i className="fa fa-trash" />
        </button>
    </Link>
)

export default StartOverButton
