import { connect } from "react-redux"
import misago from "limitless/index"
import { Snackbar, select } from "limitless/components/snackbar"
import mount from "limitless/utils/mount-component"

export default function initializer() {
  mount(connect(select)(Snackbar), "snackbar-mount")
}

misago.addInitializer({
  name: "component:snackbar",
  initializer: initializer,
  after: "snackbar"
})
