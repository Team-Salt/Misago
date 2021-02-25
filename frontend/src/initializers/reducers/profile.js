import misago from "limitless/index"
import reducer from "limitless/reducers/profile"
import store from "limitless/services/store"

export default function initializer() {
  store.addReducer("profile", reducer, {})
}

misago.addInitializer({
  name: "reducer:profile",
  initializer: initializer,
  before: "store"
})
