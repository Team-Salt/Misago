import misago from "limitless/index"
import reducer, { hydrate } from "limitless/reducers/poll"
import store from "limitless/services/store"

export default function initializer() {
  let initialState = null
  if (misago.has("THREAD") && misago.get("THREAD").poll) {
    initialState = hydrate(misago.get("THREAD").poll)
  } else {
    initialState = {
      isBusy: false
    }
  }

  store.addReducer("poll", reducer, initialState)
}

misago.addInitializer({
  name: "reducer:poll",
  initializer: initializer,
  before: "store"
})
