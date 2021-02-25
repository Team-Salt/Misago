import { paths } from "limitless/components/thread/root"
import misago from "limitless/index"
import mount from "limitless/utils/routed-component"

export default function initializer(context) {
  if (context.has("THREAD") && context.has("POSTS")) {
    mount({
      paths: paths()
    })
  }
}

misago.addInitializer({
  name: "component:thread",
  initializer: initializer,
  after: "store"
})
