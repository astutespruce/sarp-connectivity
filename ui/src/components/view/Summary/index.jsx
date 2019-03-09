import React, { useEffect, useState } from "react"
import PropTypes from "prop-types"
import { connect } from "react-redux"

import * as actions from "../../../actions/summary"
import { FeaturePropType } from "../../../CustomPropTypes"
import { formatNumber } from "../../../utils/format"

import SummaryMap from "./Map"
import Sidebar from "../../Sidebar"
import UnitSearch from "../../UnitSearch"
import SummaryUnitDetails from "./SummaryUnitDetails"
import { LAYER_ZOOM } from "./config"

import summaryStats from "../../../data/summary_stats.json"

const Summary = ({ selectedFeature, system, type, selectFeature, setSearchFeature }) => {
    const [searchValue, setSearchValue] = useState("")

    useEffect(
        () => {
            setSearchValue("")
        },
        [system]
    )

    const { dams, barriers, miles } = summaryStats.southeast
    const total = type === "dams" ? dams : barriers

    const handleSearchChange = value => {
        setSearchValue(value)
    }

    const handleSearchSelect = item => {
        const { layer } = item
        setSearchFeature(item, LAYER_ZOOM[layer])
    }

    return (
        <React.Fragment>
            <Sidebar>
                {selectedFeature.isEmpty() ? (
                    <div id="SidebarContent">
                        <p>
                            Across the Southeast, there are at least {formatNumber(dams)} dams, resulting in an average
                            of {formatNumber(miles)} miles of connected rivers and streams.
                            <br />
                            <br />
                            Click on a summary unit the map for more information about that area.
                            <br />
                            <br />
                        </p>

                        <div>
                            <UnitSearch
                                system={system}
                                value={searchValue}
                                onChange={handleSearchChange}
                                onSelect={handleSearchSelect}
                            />
                        </div>

                        <p className="has-text-grey">
                            <br />
                            <br />
                            Note: These statistics are based on <i>inventoried</i> dams. Because the inventory is
                            incomplete in many areas, areas with a high number of dams may simply represent areas that
                            have a more complete inventory.
                        </p>
                    </div>
                ) : (
                    <SummaryUnitDetails
                        selectedFeature={selectedFeature}
                        total={total}
                        type={type}
                        meanConnectedMiles={miles}
                        onClose={() => selectFeature(selectedFeature.clear())}
                    />
                )}
            </Sidebar>
            <div id="MapContainer">
                <SummaryMap />
            </div>
        </React.Fragment>
    )
}

Summary.propTypes = {
    selectedFeature: FeaturePropType.isRequired,
    type: PropTypes.string.isRequired,
    system: PropTypes.string.isRequired,
    selectFeature: PropTypes.func.isRequired,
    setSearchFeature: PropTypes.func.isRequired
}

const mapStateToProps = globalState => {
    const state = globalState.get("summary")

    return {
        system: state.get("system"),
        type: state.get("type"),
        selectedFeature: state.get("selectedFeature")
    }
}

export default connect(
    mapStateToProps,
    actions
)(Summary)
