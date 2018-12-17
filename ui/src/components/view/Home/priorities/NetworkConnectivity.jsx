import React from "react"

import Section from "../Section"

import { scrollIntoView } from "../../../../utils/dom"

function NetworkConnectivity() {
    return (
        <Section id="NetworkConnectivityDef" title="Network Connectivity">
            <p>
                Aquatic barriers prioritized according to network connectivity are driven exclusively on the total
                amount of functional aquatic network that would be reconnected if a given dam was removed. This is
                driven by the&nbsp;
                <a onClick={() => scrollIntoView("NetworkLengthDef")}>network length</a> metric. No consideration is
                given to other characteristics that measure the quality and condition of those networks.
                <br />
                <br />
                This prioritization will be most useful for you if your aquatic restoration goals are driven by the
                amount of connected aquatic network you are able to gain by removing aquatic barriers. For example, some
                species require a minimum network length in order to thrive and this prioritization would provide you
                with information on which barriers would be of greater priority based on the number of miles
                reconnected. <br />
                <br />
                Note: this scenario may result in dams with large reservoirs being ranked highly due to the large amount
                of upstream length that may be associated with these dams. However, these dams may not be particularly
                feasible to remove.
            </p>
        </Section>
    )
}

export default NetworkConnectivity
