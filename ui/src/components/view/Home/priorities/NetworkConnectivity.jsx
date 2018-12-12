import React from "react"

import Section from "../Section"

import { scrollIntoView } from "../../../../utils/dom"

function NetworkConnectivity() {
    return (
        <Section id="NetworkConnectivityDef" title="Network Connectivity">
            <p>
                Aquatic barriers prioritized according to network connectivity are driven exclusively based on the total
                amount of functional aquatic network that would be reconnected if they were removed. This is driven by
                the&nbsp;
                <a onClick={() => scrollIntoView("NetworkLengthDef")}>network length</a> metric. No consideration is
                given to other characteristics that measure the quality and condition of those networks.
                <br />
                <br />
                This prioritization will be most useful for you if your aquatic restoration goals are driven largely by the amount of
                connected aquatic network you are able to gain by removing aquatic barriers.
            </p>
        </Section>
    )
}

export default NetworkConnectivity
