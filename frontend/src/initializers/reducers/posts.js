import misago from "limitless/index"
import reducer, { hydrate } from "limitless/reducers/posts"
import store from "limitless/services/store"

export default function initializer() {
  let initialState = null
  if (misago.has("POSTS")) {
    initialState = hydrate(misago.get("POSTS"))
  } else {
    initialState = {
      isLoaded: false,
      isBusy: false
    }
  }

  store.addReducer("posts", reducer, initialState)
}

misago.addInitializer({
  name: "reducer:posts",
  initializer: initializer,
  before: "store"
})
