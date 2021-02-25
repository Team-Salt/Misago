import Options, { paths } from "limitless/components/options/root"
import misago from "limitless/index"
import mount from "limitless/utils/routed-component"

export default function initializer(context) {
  if (context.has("USER_OPTIONS")) {
    mount({
      root: misago.get("USERCP_URL"),
      component: Options,
      paths: paths()
    })
  }
}

misago.addInitializer({
  name: "component:options",
  initializer: initializer,
  after: "store"
})
