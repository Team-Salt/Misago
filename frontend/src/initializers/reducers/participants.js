import misago from "limitless/index"
import reducer from "limitless/reducers/participants"
import store from "limitless/services/store"

export default function initializer() {
  let initialState = null
  if (misago.has("THREAD")) {
    initialState = misago.get("THREAD").participants
  }

  store.addReducer("participants", reducer, initialState || [])
}

misago.addInitializer({
  name: "reducer:participants",
  initializer: initializer,
  before: "store"
})
