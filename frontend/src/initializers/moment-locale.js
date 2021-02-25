import moment from "moment"
import misago from "limitless/index"

export default function initializer() {
  moment.locale($("html").attr("lang"))
}

misago.addInitializer({
  name: "moment",
  initializer: initializer
})
