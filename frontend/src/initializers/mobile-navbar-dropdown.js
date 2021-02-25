import misago from "limitless/index"
import dropdown from "limitless/services/mobile-navbar-dropdown"

export default function initializer() {
  let element = document.getElementById("mobile-navbar-dropdown-mount")
  if (element) {
    dropdown.init(element)
  }
}

misago.addInitializer({
  name: "dropdown",
  initializer: initializer,
  before: "store"
})
