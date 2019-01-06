export const scrollIntoView = (id, behavior = "auto") => {
    const elem = window.document.getElementById(id)
    if (elem) {
        elem.scrollIntoView({ behavior, block: "start" })
    }
}

export default { scrollIntoView }
