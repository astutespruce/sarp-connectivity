import React from "react"
import { Link } from "react-router-dom"

import CBILogo from "../../../img/cbi_logo.png"

function Credits() {
    return (
        <React.Fragment>
            <section>
                <div className="columns">
                    <div className="column is-two-thirds">
                        <h3 className="subtitle is-3" style={{ marginBottom: 0 }}>
                            Get involved!
                        </h3>
                        <p>
                            You can help improve the inventory by sharing data, assisting with field reconnaissance to
                            evaluate the impact of aquatic barriers, joining an{" "}
                            <Link to="/teams">Aquatic Connectivity Team</Link>, or even by reporting issues with the
                            inventory data in this tool.
                            <br />
                            <br />
                            <a href="mailto:kat@southeastaquatics.net">Contact us</a> to learn more about how you can
                            help improve aquatic connectivity in the Southeast.
                        </p>
                    </div>
                    <div className="column">
                        <h3 className="subtitle is-3 no-margin">Need Help?</h3>
                        <p>
                            If you are not able to get what you need from this tool or if you need to report an issue,
                            please&nbsp;
                            <a href="mailto:kat@southeastaquatics.net">let us know</a>!
                        </p>
                    </div>
                </div>
            </section>
            <section id="ContentPageFooter">
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
            </section>
        </React.Fragment>
    )
}

export default Credits
