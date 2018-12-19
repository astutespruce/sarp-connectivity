import React from "react"

import Section from "../../../Section"

import { ReactComponent as HighLengthIcon } from "../../../../img/length_high.svg"
import { ReactComponent as LowLengthIcon } from "../../../../img/length_low.svg"

function NetworkLength() {
    return (
        <Section id="NetworkLengthDef" title="Network Length">
            <p>
                Network length measures the amount of connected aquatic network length that would be added to the
                network by removing the barrier. It is the smaller of either the total upstream network length or total
                downstream network length for the networks subdivided by this barrier. This is because a barrier may
                have a very large upstream network, but if there is another barrier immediately downstream, the overall
                effect of removing this barrier will be quite small.
            </p>
            <div className="prioritization-details flex-container flex-justify-space-between">
                <div>
                    <HighLengthIcon />
                    <h4 className="is-size-4 text-align-center">High Network Length</h4>
                    <p>
                        Barriers that have large upstream and downstream networks will contribute a large amount of
                        connected aquatic network length if they are removed.
                    </p>
                </div>
                <div>
                    <LowLengthIcon />
                    <h4 className="is-size-4 text-align-center">Low Network Length</h4>
                    <p>
                        Barriers that have small upstream or downstream networks contribute relatively little connected
                        aquatic network length if removed.
                    </p>
                </div>
            </div>
            <h5 className="title is-5">Methods:</h5>
            <ol>
                <li>
                    The total upstream length is calculated as the sum of the lengths of all upstream river and stream
                    reaches.
                </li>
                <li>
                    The total downstream length is calculated for the network immediately downstream of the barrier.
                    Note: this is the total network length of the downstream network, <i>not</i> the shortest downstream
                    path to the next barrier or river mouth.
                </li>
                <li>Network length is the smaller of the upstream or downstream network lengths.</li>
            </ol>
        </Section>
    )
}

export default NetworkLength
