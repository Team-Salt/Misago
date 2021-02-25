import misago from "limitless/index"
import storage from "limitless/services/local-storage"

export default function initializer() {
  storage.init("misago_")
}

misago.addInitializer({
  name: "local-storage",
  initializer: initializer
})
