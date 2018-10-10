import React from "react"
import { ReactComponent as Logo } from "../../img/logo.svg"

const NotFound = () => (
    <div id="NotFound" className="flex-container-column text-align-center flex-align-center">
        <h1 className="is-size-1">Oops!</h1>
        <h2 className="is-size-3">We could not find the fish you were looking for.</h2>
        <Logo />
    </div>
)

export default NotFound
