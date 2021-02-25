import misago from "limitless/index"
import auth from "limitless/services/auth"
import modal from "limitless/services/modal"
import store from "limitless/services/store"
import storage from "limitless/services/local-storage"

export default function initializer() {
  auth.init(store, storage, modal)
}

misago.addInitializer({
  name: "auth",
  initializer: initializer,
  after: "store"
})
