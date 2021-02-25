import misago from "limitless/index"
import store from "limitless/services/store"

export default function initializer() {
  store.init()
}

misago.addInitializer({
  name: "store",
  initializer: initializer,
  before: "_end"
})
