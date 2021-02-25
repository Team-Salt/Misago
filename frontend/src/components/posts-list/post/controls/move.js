import React from "react"
import Button from "limitless/components/button"
import Form from "limitless/components/form"
import FormGroup from "limitless/components/form-group"
import * as post from "limitless/reducers/post"
import ajax from "limitless/services/ajax"
import modal from "limitless/services/modal"
import snackbar from "limitless/services/snackbar"
import store from "limitless/services/store"

export default class extends Form {
  constructor(props) {
    super(props)

    this.state = {
      isLoading: false,

      url: "",

      validators: {
        url: []
      },
      errors: {}
    }
  }

  clean() {
    if (!this.state.url.trim().length) {
      snackbar.error(gettext("You have to enter link to the other thread."))
      return false
    }

    return true
  }

  send() {
    return ajax.post(this.props.thread.api.posts.move, {
      new_thread: this.state.url,
      posts: [this.props.post.id]
    })
  }

  handleSuccess(success) {
    store.dispatch(
      post.patch(this.props.post, {
        isDeleted: true
      })
    )

    modal.hide()

    snackbar.success(gettext("Selected post was moved to the other thread."))
  }

  handleError(rejection) {
    if (rejection.status === 400) {
      snackbar.error(rejection.detail)
    } else {
      snackbar.apiError(rejection)
    }
  }

  onUrlChange = event => {
    this.changeValue("url", event.target.value)
  }

  render() {
    return (
      <div className="modal-dialog" role="document">
        <form onSubmit={this.handleSubmit}>
          <div className="modal-content">
            <ModalHeader />
            <div className="modal-body">
              <FormGroup
                for="id_url"
                label={gettext("Link to thread you want to move post to")}
              >
                <input
                  className="form-control"
                  disabled={this.state.isLoading}
                  id="id_url"
                  onChange={this.onUrlChange}
                  value={this.state.url}
                />
              </FormGroup>
            </div>
            <div className="modal-footer">
              <button
                className="btn btn-primary"
                loading={this.state.isLoading}
              >
                {gettext("Move post")}
              </button>
            </div>
          </div>
        </form>
      </div>
    )
  }
}

export function ModalHeader(props) {
  return (
    <div className="modal-header">
      <button
        aria-label={gettext("Close")}
        className="close"
        data-dismiss="modal"
        type="button"
      >
        <span aria-hidden="true">&times;</span>
      </button>
      <h4 className="modal-title">{gettext("Move post")}</h4>
    </div>
  )
}
