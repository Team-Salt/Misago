import misago from "limitless/index"
import { doTick } from "limitless/reducers/tick"
import store from "limitless/services/store"

const TICK_PERIOD = 50 * 1000 //do the tick every 50s

export default function initializer() {
  window.setInterval(function() {
    store.dispatch(doTick())
  }, TICK_PERIOD)
}

misago.addInitializer({
  name: "tick-start",
  initializer: initializer,
  after: "store"
})
