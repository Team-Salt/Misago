import { connect } from "react-redux"
import Profile, { paths, select } from "limitless/components/profile/root"
import misago from "limitless/index"
import mount from "limitless/utils/routed-component"

export default function initializer(context) {
  if (context.has("PROFILE") && context.has("PROFILE_PAGES")) {
    mount({
      root: misago.get("PROFILE").url,
      component: connect(select)(Profile),
      paths: paths()
    })
  }
}

misago.addInitializer({
  name: "component:profile",
  initializer: initializer,
  after: "reducer:profile-hydrate"
})
