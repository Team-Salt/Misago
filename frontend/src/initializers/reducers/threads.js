import misago from "limitless/index"
import reducer from "limitless/reducers/threads"
import store from "limitless/services/store"

export default function initializer() {
  store.addReducer("threads", reducer, [])
}

misago.addInitializer({
  name: "reducer:threads",
  initializer: initializer,
  before: "store"
})
