import Raven from "raven-js"

export const logException = (ex, context) => {
    Raven.captureException(ex, {
        extra: context
    })
    /* eslint no-console:0 */
    window.console && console.error && console.error(ex)
}

export default { logException }
