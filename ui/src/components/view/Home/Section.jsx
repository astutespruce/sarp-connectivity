import React from "react"
import PropTypes from "prop-types"

const Section = ({ children, dark, title, subtitle, id, className }) => (
    <section id={id} className={`${className || ""} container ${dark ? "dark" : ""}`}>
        <div className="hero container">
            <div className="hero-body">
                {title && <h1 className="title">{title}</h1>}
                {subtitle && <h2 className="subtitle">{subtitle}</h2>}
                {children}
            </div>
        </div>
    </section>
)

Section.propTypes = {
    children: PropTypes.oneOfType([PropTypes.arrayOf(PropTypes.node), PropTypes.node]).isRequired,

    dark: PropTypes.bool,
    title: PropTypes.string,
    subtitle: PropTypes.string,
    id: PropTypes.string,
    className: PropTypes.string
}

Section.defaultProps = {
    dark: false,
    title: null,
    subtitle: null,
    id: null,
    className: null
}

export default Section
