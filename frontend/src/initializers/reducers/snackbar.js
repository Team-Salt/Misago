import misago from "limitless/index"
import reducer, { initialState } from "limitless/reducers/snackbar"
import store from "limitless/services/store"

export default function initializer() {
  store.addReducer("snackbar", reducer, initialState)
}

misago.addInitializer({
  name: "reducer:snackbar",
  initializer: initializer,
  before: "store"
})
