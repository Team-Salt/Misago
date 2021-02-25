import misago from "limitless"
import reducer, { initialState } from "limitless/reducers/search"
import store from "limitless/services/store"

export default function initializer() {
  store.addReducer(
    "search",
    reducer,
    Object.assign({}, initialState, {
      providers: misago.get("SEARCH_PROVIDERS") || [],
      query: misago.get("SEARCH_QUERY") || ""
    })
  )
}

misago.addInitializer({
  name: "reducer:search",
  initializer: initializer,
  before: "store"
})
