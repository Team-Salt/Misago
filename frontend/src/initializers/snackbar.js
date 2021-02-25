import misago from "limitless/index"
import snackbar from "limitless/services/snackbar"
import store from "limitless/services/store"

export default function initializer() {
  snackbar.init(store)
}

misago.addInitializer({
  name: "snackbar",
  initializer: initializer,
  after: "store"
})
