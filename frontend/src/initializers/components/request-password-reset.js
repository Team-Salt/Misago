import misago from "limitless/index"
import RequestPasswordReset from "limitless/components/request-password-reset"
import mount from "limitless/utils/mount-component"

export default function initializer() {
  if (document.getElementById("request-password-reset-mount")) {
    mount(RequestPasswordReset, "request-password-reset-mount", false)
  }
}

misago.addInitializer({
  name: "component:request-password-reset",
  initializer: initializer,
  after: "store"
})
