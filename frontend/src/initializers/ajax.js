import misago from "limitless/index"
import ajax from "limitless/services/ajax"

export default function initializer() {
  ajax.init(misago.get("CSRF_COOKIE_NAME"))
}

misago.addInitializer({
  name: "ajax",
  initializer: initializer
})
