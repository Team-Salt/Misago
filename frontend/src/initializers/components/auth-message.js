import { connect } from "react-redux"
import misago from "limitless/index"
import AuthMessage, { select } from "limitless/components/auth-message"
import mount from "limitless/utils/mount-component"

export default function initializer() {
  mount(connect(select)(AuthMessage), "auth-message-mount")
}

misago.addInitializer({
  name: "component:auth-message",
  initializer: initializer,
  after: "store"
})
