import misago from "limitless/index"
import reducer, { hydrate } from "limitless/reducers/thread"
import store from "limitless/services/store"

export default function initializer() {
  let initialState = null
  if (misago.has("THREAD")) {
    initialState = hydrate(misago.get("THREAD"))
  } else {
    initialState = {
      isBusy: false
    }
  }

  store.addReducer("thread", reducer, initialState)
}

misago.addInitializer({
  name: "reducer:thread",
  initializer: initializer,
  before: "store"
})
