import React from "react"
import Section from "../../Section"

// Photo by Robert Zunikoff on Unsplash, https://unsplash.com/photos/ko7Tp_LyAt4
import WaterStonesImage from "../../../img/robert-zunikoff-409755-unsplash.jpg"

function UseCases() {
    return (
        <React.Fragment>
            <Section title="Example use case: regional planning">
                <p>
                    You can also use this tool to better understand the number and location of aquatic barriers across
                    the southeastern U.S. You can use this information to guide regional planning and allocate resources
                    targeted at improving aquatic conditions. You can use this information to help stakeholders and
                    others understand the impact of aquatic barriers across the region, and build awareness about how to
                    reduce those impacts…
                </p>
            </Section>
            <Section
                image={WaterStonesImage}
                dark
                title="Example use case: removing small, unneeded dams on private land"
            >
                <p>
                    One way you can use this tool is to identify and prioritize dams according to the criteria that
                    matter to you. For example, you can first select the dams that are within the watersheds where you
                    work. Then you can filter those dams further to find those that have a low height, are on private
                    land, and were constructed a long time ago. These dams may no longer be necessary, but since they
                    haven’t been targeted for removal, they may remain barriers within the aquatic network. Once you’ve
                    selected the dams that meet your criteria, you can re-prioritize these to find those that would
                    contribute most to restoring overall aquatic connectivity. You can explore these further using the
                    interactive map, or you can export them to a spreadsheet for further analysis and exploration. You
                    can use this information to supplement your grant proposals and work plans to…
                </p>
            </Section>
        </React.Fragment>
    )
}

export default UseCases
