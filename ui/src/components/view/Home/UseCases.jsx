import React from "react"

// Photo by Robert Zunikoff on Unsplash, https://unsplash.com/photos/ko7Tp_LyAt4
// import WaterStonesImage from "../../../img/robert-zunikoff-409755-unsplash.jpg"

// photo from: https://www.nature.org/en-us/about-us/where-we-work/united-states/tennessee/stories-in-tennessee/dam-removal-opens-up-roaring-river/
import roaringRiverDamImage from "../../../img/Roaring_River_Dam_Removal_-_digging_-_Paul_Kingsbury_TNC_P1030732.jpg"

function UseCases() {
    return (
        <section>
            <h3 className="title is-3">Example: prioritizing a failing dam for removal</h3>
            <p>
                The Southeast Aquatic Barriers Inventory enabled partners in Tennessee to identify and prioritize an
                aging dam for removal. At 220 feet wide and 15 tall, this dam is the largest removed in Tennessee for
                river and stream restoration.
                <br />
                <br />
            </p>
            <img src={roaringRiverDamImage} alt="Roaring River Dam Removal" />
            <div className="is-size-7 has-text-grey">
                Photo:{" "}
                <a
                    href="https://www.nature.org/en-us/about-us/where-we-work/united-states/tennessee/stories-in-tennessee/dam-removal-opens-up-roaring-river/"
                    target="_blank"
                    rel="noopener noreferrer"
                >
                    Roaring River Dam Removal, Tennessee, 2017. © Paul Kingsbury, The Nature Conservancy.
                </a>
            </div>
            <p>
                <br />
                <br />
                Built in 1976 by the U.S. Army Corps of Engineers to keep reservoir fish species from migrating
                upstream, partners determined that this deteriorating dam no longer met its original purpose. Instead of
                repairing the dam, partners decided that it would be better to remove the dam altogether in order to
                restore aquatic connectivity. Partners working on this project included the Tennessee Wildlife Resources
                Agency, the U.S. Army Corps of Engineers, The Nature Conservancy, the U.S. Fish and Wildlife Service,
                and the Southeast Aquatic Resources Partnership.
            </p>
        </section>
    )
}

export default UseCases
