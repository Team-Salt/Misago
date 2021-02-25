import misago from "limitless/index"
import include from "limitless/services/include"
import zxcvbn from "limitless/services/zxcvbn"

export default function initializer() {
  zxcvbn.init(include)
}

misago.addInitializer({
  name: "zxcvbn",
  initializer: initializer
})
