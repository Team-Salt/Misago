import misago from "limitless/index"
import reducer from "limitless/reducers/username-history"
import store from "limitless/services/store"

export default function initializer() {
  store.addReducer("username-history", reducer, [])
}

misago.addInitializer({
  name: "reducer:username-history",
  initializer: initializer,
  before: "store"
})
