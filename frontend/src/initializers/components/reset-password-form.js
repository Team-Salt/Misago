import misago from "limitless"
import ResetPasswordForm from "limitless/components/reset-password-form"
import mount from "limitless/utils/mount-component"

export default function initializer() {
  if (document.getElementById("reset-password-form-mount")) {
    mount(ResetPasswordForm, "reset-password-form-mount", false)
  }
}

misago.addInitializer({
  name: "component:reset-password-form",
  initializer: initializer,
  after: "store"
})
