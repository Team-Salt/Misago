import misago from "limitless/index"
import { patch } from "limitless/reducers/auth"
import ajax from "limitless/services/ajax"
import snackbar from "limitless/services/snackbar"
import store from "limitless/services/store"

const AUTH_SYNC_RATE = 45 // sync user with backend every 45 seconds

export default function initializer(context) {
  if (context.get("isAuthenticated")) {
    window.setInterval(function() {
      ajax.get(context.get("AUTH_API")).then(
        function(data) {
          store.dispatch(patch(data))
        },
        function(rejection) {
          snackbar.apiError(rejection)
        }
      )
    }, AUTH_SYNC_RATE * 1000)
  }
}

misago.addInitializer({
  name: "auth-sync",
  initializer: initializer,
  after: "auth"
})
