import React from "react"

import Section from "../Section"

import { scrollIntoView } from "../../../../utils/dom"

function WatershedCondition() {
    return (
        <Section id="WatershedConditionDef" title="Watershed Condition">
            <p>
                Aquatic barriers prioritized according to watershed condition are driven by metrics related to the
                overall quality of the aquatic network that would be reconnected if they were removed. It is based on a
                combination of&nbsp;
                <a onClick={() => scrollIntoView("NetworkComplexityDef")}>network complexity</a>
                ,&nbsp;
                <a onClick={() => scrollIntoView("NetworkSinuosityDef")}>network sinuosity</a>, and&nbsp;
                <a onClick={() => scrollIntoView("NaturalLandcoverDef")}>floodplain natural landcover</a>. Each of these
                metrics is weighted equally. No consideration is given to total network length, though network length
                and network complexity tend to be correlated with each other.
                <br />
                <br />
                This prioritization will be most useful for you if your aquatic restoration goals are driven largely by
                the overall quality of connected aquatic network you are able to gain by removing aquatic barriers.
            </p>
        </Section>
    )
}

export default WatershedCondition
