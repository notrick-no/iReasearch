const resize = (el) => {
  if (!(el instanceof HTMLTextAreaElement)) return
  el.style.height = 'auto'
  el.style.height = `${el.scrollHeight}px`
}

export default {
  mounted(el) {
    if (!(el instanceof HTMLTextAreaElement)) return
    el.style.overflowY = 'hidden'
    const handler = () => resize(el)
    el.__autoResizeHandler = handler
    el.addEventListener('input', handler)
    resize(el)
  },
  updated(el) {
    resize(el)
  },
  beforeUnmount(el) {
    if (!(el instanceof HTMLTextAreaElement)) return
    if (el.__autoResizeHandler) {
      el.removeEventListener('input', el.__autoResizeHandler)
      delete el.__autoResizeHandler
    }
  },
}
