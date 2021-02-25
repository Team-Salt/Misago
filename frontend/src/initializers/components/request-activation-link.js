import misago from "limitless/index"
import RequestActivationLink from "limitless/components/request-activation-link"
import mount from "limitless/utils/mount-component"

export default function initializer() {
  if (document.getElementById("request-activation-link-mount")) {
    mount(RequestActivationLink, "request-activation-link-mount", false)
  }
}

misago.addInitializer({
  name: "component:request-activation-link",
  initializer: initializer,
  after: "store"
})
