import misago from "limitless/index"
import reducer from "limitless/reducers/selection"
import store from "limitless/services/store"

export default function initializer() {
  store.addReducer("selection", reducer, [])
}

misago.addInitializer({
  name: "reducer:selection",
  initializer: initializer,
  before: "store"
})
