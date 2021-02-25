import paths from "limitless/components/search"
import misago from "limitless"
import mount from "limitless/utils/routed-component"

export default function initializer(context) {
  if (context.get("CURRENT_LINK") === "limitless:search") {
    mount({
      paths: paths(misago.get("SEARCH_PROVIDERS"))
    })
  }
}

misago.addInitializer({
  name: "component:search",
  initializer: initializer,
  after: "store"
})
