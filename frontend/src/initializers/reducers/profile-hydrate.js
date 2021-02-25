import misago from "limitless/index"
import { hydrate } from "limitless/reducers/profile"
import store from "limitless/services/store"

export default function initializer() {
  if (misago.has("PROFILE")) {
    store.dispatch(hydrate(misago.get("PROFILE")))
  }
}

misago.addInitializer({
  name: "reducer:profile-hydrate",
  initializer: initializer,
  after: "store"
})
