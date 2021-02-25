import misago from "limitless/index"
import reducer from "limitless/reducers/users"
import store from "limitless/services/store"

export default function initializer() {
  store.addReducer("users", reducer, [])
}

misago.addInitializer({
  name: "reducer:users",
  initializer: initializer,
  before: "store"
})
