import React from "react"

import Section from "./Section"

import { ReactComponent as FunctionalNetwork } from "../../../img/functional_network.svg"

// Photo from: https://www.flickr.com/photos/savannahcorps/9272554306/
import DamImage2 from "../../../img/9272554306_b34bf886f4_z.jpg"

// Photo from: https://www.flickr.com/photos/usfwssoutheast/33643110826/in/album-72157675681441135/
import CaneRiverDam from "../../../img/33643110826_a90387d592_z.jpg"


function Concepts() {
    return (
        <React.Fragment>
            <Section title="Key Concept: Aquatic Barriers">
                <div className="columns">
                    <div className="column">
                        <p>
                            These barriers are natural and human-made structures that impede the passage of aquatic
                            organisms through the river network. Some human-made barriers may no longer serve their
                            original purpose and have fallen into disrepair. These barriers may be particularly good
                            candidates for removal or remediation to restore aquatic connectivity.
                            <br />
                            <br />
                            Aquatic barriers include:
                        </p>
                        <ul>
                            <li>Waterfalls (from the USGS Waterfalls Inventory)</li>
                            <li>Dams</li>
                            <li>Road-related barriers (culverts, fords, and similar potential aquatic barriers)</li>
                        </ul>
                        <p>
                            <br />
                            Not all barriers completely block the passage of all aquatic organisms. In this
                            tool waterfalls and dams are considered &quot;hard&quot; barriers that divide the aquatic
                            network.  Road-related barriers require field reconnaissance to determine if they are true barriers in the aquatic network.  
                        </p>
                    </div>
                    <div className="column">
                        <img src={CaneRiverDam} alt="Cane River Dam Ruins" className="photo" />
                        <img src={DamImage2} alt="Hartwell Dam" className="photo" style={{ marginTop: "3rem" }} />
                    </div>
                </div>
            </Section>
            <Section title="Key Concept: Functional Networks">
                <div className="columns">
                    <div className="column is-two-thirds">
                        <p>
                            Functional networks are the stream and river reaches that extend upstream from a barrier or
                            river mouth to either the origin of that stream or the next upstream barrier. They form the
                            basis for the aquatic network metrics used in this tool.
                            <br />
                            <br />
                            To calculate functional networks, all barriers were snapped to the&nbsp;
                            <a
                                href="https://www.usgs.gov/core-science-systems/ngp/national-hydrography/nhdplus-high-resolution"
                                target="_blank"
                                rel="noopener noreferrer"
                            >
                                USGS High Resolution National Hydrography Dataset
                            </a>
                            &nbsp; (NHDPlus) for all areas except the lower Mississipi (hydrologic region 8), where the
                            NHDPlus Medium Resolution version was the only one available. Where possible, their
                            locations were manually inspected to verify their correct position on the aquatic network.
                            <br />
                            <br />
                            <span className="icon">
                                <i className="fas fa-exclamation-triangle" />
                            </span>
                            Note: due to limitations of existing data sources for aquatic networks, not all aquatic
                            barriers can be correctly located on the aquatic networks. These barriers are not included
                            in the network connectivity analysis and cannot be prioritized using this tool. However,
                            these data can still be downloaded from this tool and used for offline analysis.
                        </p>
                    </div>
                    <div className="column">
                        <FunctionalNetwork style={{ height: "30rem" }} />
                    </div>
                </div>
            </Section>
        </React.Fragment>
    )
}

export default Concepts
