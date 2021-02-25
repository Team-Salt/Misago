import misago from "limitless/index"
import title from "limitless/services/page-title"

export default function initializer(context) {
  title.init(
    context.get("SETTINGS").forum_index_title,
    context.get("SETTINGS").forum_name
  )
}

misago.addInitializer({
  name: "page-title",
  initializer: initializer
})
