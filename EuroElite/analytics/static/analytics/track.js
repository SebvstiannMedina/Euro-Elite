function sendEvent(name, props = {}) {
  try {
    fetch('/analytics/track/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({name: name, props: props})
    }).catch(function(e){
      console.warn('analytics send failed', e)
    })
  } catch(e) {
    console.warn('analytics error', e)
  }
}

// ejemplo automático: trackear clicks en botones con data-event
document.addEventListener('click', function(e){
  var el = e.target.closest && e.target.closest('[data-event]')
  if (!el) return
  var name = el.getAttribute('data-event')
  var props = {}
  try {
    var json = el.getAttribute('data-props')
    if (json) props = JSON.parse(json)
  } catch(e){}
  sendEvent(name, props)
})
