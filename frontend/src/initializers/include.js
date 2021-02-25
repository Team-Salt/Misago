import misago from "limitless/index"
import include from "limitless/services/include"

export default function initializer(context) {
  include.init(context.get("STATIC_URL"))
}

misago.addInitializer({
  name: "include",
  initializer: initializer
})
