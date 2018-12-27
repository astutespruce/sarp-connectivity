import React from "react"

import Section from "../../Section"

import CBILogo from "../../../img/cbi_logo.png"

function Credits() {
    return (
        <Section id="ContentPageFooter">
            <div className="columns">
                <div className="column is-two-thirds">
                    <p>
                        This application was created by the&nbsp;
                        <a href="https://consbio.org" target="_blank" rel="noopener noreferrer">
                            Conservation Biology Institute
                        </a>
                        &nbsp; (CBI) in partnership with the&nbsp;
                        <a href="https://southeastaquatics.net/" target="_blank" rel="noopener noreferrer">
                            Southeast Aquatic Resources Partnership
                        </a>
                        . CBI provides science and software development to support the conservation of biodiversity.
                    </p>
                </div>
                <div className="column">
                    <img src={CBILogo} style={{ height: 48 }} alt="CBI logo" />
                </div>
            </div>
            <p>
                This project was supported in part by grants from the&nbsp;
                <a href="https://www.fws.gov/fisheries/fish-passage.html" target="_blank" rel="noopener noreferrer">
                    U.S. Fish and Wildlife Service Fish Passage Program
                </a>
                , the&nbsp;
                <a href="https://gcpolcc.org/" target="_blank" rel="noopener noreferrer">
                    Gulf Coastal Plains and Ozarks Landscape Conservation Cooperative
                </a>
                , and the&nbsp;
                <a
                    href="https://myfwc.com/conservation/special-initiatives/fwli/grant/"
                    target="_blank"
                    rel="noopener noreferrer"
                >
                    Florida State Wildlife Grants Program
                </a>
                .
            </p>
        </Section>
    )
}

export default Credits
