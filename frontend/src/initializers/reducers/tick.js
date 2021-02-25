import misago from "limitless/index"
import reducer, { initialState } from "limitless/reducers/tick"
import store from "limitless/services/store"

export default function initializer() {
  store.addReducer("tick", reducer, initialState)
}

misago.addInitializer({
  name: "reducer:tick",
  initializer: initializer,
  before: "store"
})
