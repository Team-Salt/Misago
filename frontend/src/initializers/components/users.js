import Users, { paths } from "limitless/components/users/root"
import misago from "limitless/index"
import mount from "limitless/utils/routed-component"

export default function initializer(context) {
  if (context.has("USERS_LISTS")) {
    mount({
      root: misago.get("USERS_LIST_URL"),
      component: Users,
      paths: paths()
    })
  }
}

misago.addInitializer({
  name: "component:users",
  initializer: initializer,
  after: "store"
})
