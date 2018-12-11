export const scrollIntoView = id => {
    const elem = window.document.getElementById(id)
    if (elem) {
        elem.scrollIntoView()
    }
}

export default { scrollIntoView }
