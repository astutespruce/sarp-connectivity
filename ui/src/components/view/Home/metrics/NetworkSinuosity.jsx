import React from "react"

import Section from "../../../Section"

import { ReactComponent as HighSinuosityIcon } from "../../../../img/sinuosity_high.svg"
import { ReactComponent as LowSinuosityIcon } from "../../../../img/sinuosity_low.svg"

function NetworkSinuosity() {
    return (
        <Section id="NetworkSinuosityDef" title="Network Sinuosity">
            <p>
                Network sinuosity is a measure of how much the path of the river or stream deviates from a straight
                line. In general, rivers and streams that are more sinuous generally indicate those that have lower
                alteration from human disturbance such as channelization and diking, whereas rivers that have been
                extensively altered tend to be less sinuous. Sinuosity ranges from low (&lt;1.2) to moderate (1.2 - 1.5)
                to high (&gt;1.5) (Rosgen, 1996).
            </p>
            <div className="prioritization-details flex-container flex-justify-space-between">
                <div>
                    <HighSinuosityIcon />
                    <h4 className="is-size-4 text-align-center">High Sinuosity</h4>
                    <p>
                        Rivers and streams with high sinuosity are likely less altered by artificial channelization and
                        may have a wider variety of in-stream habitat. Barriers with more sinuous upstream networks may
                        contribute more natural habitat if removed.
                    </p>
                </div>
                <div>
                    <LowSinuosityIcon />
                    <h4 className="is-size-4 text-align-center">Low Sinuosity</h4>
                    <p>
                        Rivers and streams with lower sinuosity may be more altered by artificial channelization and may
                        have a lower variety of in-stream habitat. Barriers with less sinuous upstream networks may
                        contribute less natural habitat if removed.
                    </p>
                </div>
            </div>
            <h5 className="title is-5">Methods:</h5>
            <ol>
                <li>
                    The sinuosity of each stream is calculated as the ratio between the length of that reach and the
                    straight line distance between the endpoints of that reach. The greater the total length compared to
                    the straight line distance, the higher the sinuosity.
                </li>
                <li>
                    Reaches are combined using a length-weighted average to calculate the overall sinuosity of each
                    functional network.
                </li>
            </ol>
            <h5 className="title is-5">References:</h5>
            <ul style={{ listStyle: "none" }}>
                <li>Rosgen, David L. 1996. Applied river morphology. Pagosa Springs, Colo: Wildland Hydrology.</li>
            </ul>
        </Section>
    )
}

export default NetworkSinuosity
