import React from "react"
import PropTypes from "prop-types"
import { connect } from "react-redux"

import Sidebar from "../components/Sidebar"
import FiltersList from "../components/view/Priority/FiltersList"
import * as actions from "../actions/priority"

function TestFilter({ fetchQuery }) {
    return (
        <Sidebar>
            <button className="button" type="button" onClick={() => fetchQuery("State", [{ id: "Alabama" }])}>
                Load Alabama!
            </button>
            <FiltersList />
        </Sidebar>
    )
}

TestFilter.propTypes = {
    fetchQuery: PropTypes.func.isRequired
}

export default connect(
    () => ({}),
    actions
)(TestFilter)
