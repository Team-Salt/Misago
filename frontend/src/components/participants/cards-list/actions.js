import * as participants from "limitless/reducers/participants"
import { updateAcl } from "limitless/reducers/thread"
import misago from "limitless"
import ajax from "limitless/services/ajax"
import snackbar from "limitless/services/snackbar"
import store from "limitless/services/store"

export function leave(thread, participant) {
  ajax
    .patch(thread.api.index, [
      { op: "remove", path: "participants", value: participant.id }
    ])
    .then(
      () => {
        snackbar.success(gettext("You have left this thread."))
        window.setTimeout(() => {
          window.location = misago.get("PRIVATE_THREADS_URL")
        }, 3 * 1000)
      },
      rejection => {
        snackbar.apiError(rejection)
      }
    )
}

export function remove(thread, participant) {
  ajax
    .patch(thread.api.index, [
      { op: "remove", path: "participants", value: participant.id },
      { op: "add", path: "acl", value: 1 }
    ])
    .then(
      data => {
        store.dispatch(updateAcl(data))
        store.dispatch(participants.replace(data.participants))

        const message = gettext("%(user)s has been removed from this thread.")
        snackbar.success(
          interpolate(
            message,
            {
              user: participant.username
            },
            true
          )
        )
      },
      rejection => {
        snackbar.apiError(rejection)
      }
    )
}

export function changeOwner(thread, participant) {
  ajax
    .patch(thread.api.index, [
      { op: "replace", path: "owner", value: participant.id },
      { op: "add", path: "acl", value: 1 }
    ])
    .then(
      data => {
        store.dispatch(updateAcl(data))
        store.dispatch(participants.replace(data.participants))

        const message = gettext("%(user)s has been made new thread owner.")
        snackbar.success(
          interpolate(
            message,
            {
              user: participant.username
            },
            true
          )
        )
      },
      rejection => {
        snackbar.apiError(rejection)
      }
    )
}
