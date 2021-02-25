import misago from "limitless/index"
import ajax from "limitless/services/ajax"
import captcha from "limitless/services/captcha"
import include from "limitless/services/include"
import snackbar from "limitless/services/snackbar"

export default function initializer(context) {
  captcha.init(context, ajax, include, snackbar)
}

misago.addInitializer({
  name: "captcha",
  initializer: initializer
})
