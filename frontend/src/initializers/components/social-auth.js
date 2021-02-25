import React from "react"
import SocialAuth from "limitless/components/social-auth"
import misago from "limitless"
import mount from "limitless/utils/mount-component"

export default function initializer(context) {
  if (context.get("CURRENT_LINK") === "limitless:social-complete") {
    const props = context.get("SOCIAL_AUTH_FORM")
    mount(<SocialAuth {...props} />, "page-mount")
  }
}

misago.addInitializer({
  name: "component:social-auth",
  initializer: initializer,
  after: "store"
})
