import { connect } from "react-redux"
import Categories, { select } from "limitless/components/categories"
import misago from "limitless/index"
import mount from "limitless/utils/mount-component"

export default function initializer() {
  if (document.getElementById("categories-mount")) {
    mount(connect(select)(Categories), "categories-mount")
  }
}

misago.addInitializer({
  name: "component:categories",
  initializer: initializer,
  after: "store"
})
