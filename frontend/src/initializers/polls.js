import misago from "limitless/index"
import ajax from "limitless/services/ajax"
import snackbar from "limitless/services/snackbar"
import polls from "limitless/services/polls"

export default function initializer() {
  polls.init(ajax, snackbar)
}

misago.addInitializer({
  name: "polls",
  initializer: initializer
})
