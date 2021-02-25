import misago from "limitless/index"
import ajax from "limitless/services/ajax"
import posting from "limitless/services/posting"
import snackbar from "limitless/services/snackbar"

export default function initializer() {
  posting.init(ajax, snackbar, document.getElementById("posting-placeholder"))
}

misago.addInitializer({
  name: "posting",
  initializer: initializer
})
