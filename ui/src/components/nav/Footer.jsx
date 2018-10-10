import React from "react"
import { Link } from "react-router-dom"

const Footer = () => (
    <footer className="footer is-hidden-mobile has-text-white is-size-7">
        <div className="level">
            <div className="level-left">
                <Link to="/download">Download data</Link>
                &nbsp;&nbsp;|&nbsp;&nbsp;
                <a href="https://southeastaquatics.net/" target="_blank" rel="noopener noreferrer">
                    Southeast Aquatic Resources Partnership
                </a>
                &nbsp;&nbsp;|&nbsp;&nbsp;
                <a href="https://southeastaquatics.net/about/contact-us" target="_blank" rel="noopener noreferrer">
                    Contact Us
                </a>
            </div>
            <div className="level-right">
                Created by the&nbsp;
                <a href="https://consbio.org" target="_blank" rel="noopener noreferrer">
                    Conservation Biology Institute
                </a>
            </div>
        </div>
    </footer>
)

export default Footer
