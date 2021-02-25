import React from "react"
import misago from "limitless"
import Form from "limitless/components/form"
import { load as updatePosts } from "limitless/reducers/posts"
import { update as updateSearch } from "limitless/reducers/search"
import { hydrate as updateUsers } from "limitless/reducers/users"
import ajax from "limitless/services/ajax"
import snackbar from "limitless/services/snackbar"
import store from "limitless/services/store"

export default class extends Form {
  constructor(props) {
    super(props)

    this.state = {
      isLoading: false,

      query: props.search.query
    }
  }

  componentDidMount() {
    if (this.state.query.length) {
      this.handleSubmit()
    }
  }

  onQueryChange = event => {
    this.changeValue("query", event.target.value)
  }

  clean() {
    if (!this.state.query.trim().length) {
      snackbar.error(gettext("You have to enter search query."))
      return false
    }

    return true
  }

  send() {
    store.dispatch(
      updateSearch({
        isLoading: true
      })
    )

    return ajax.get(misago.get("SEARCH_API"), {
      q: this.state.query.trim()
    })
  }

  handleSuccess(providers) {
    store.dispatch(
      updateSearch({
        query: this.state.query.trim(),
        isLoading: false,
        providers
      })
    )

    providers.forEach(provider => {
      if (provider.id === "users") {
        store.dispatch(updateUsers(provider.results.results))
      } else if (provider.id === "threads") {
        store.dispatch(updatePosts(provider.results))
      }
    })
  }

  handleError(rejection) {
    snackbar.apiError(rejection)

    store.dispatch(
      updateSearch({
        isLoading: false
      })
    )
  }

  render() {
    return (
      <div className="page-header-bg">
        <div className="page-header page-search-form">
          <form onSubmit={this.handleSubmit}>
            <div className="container">
              <div className="row">
                <div className="col-xs-12 col-md-3">
                  <h1>{gettext("Search")}</h1>
                </div>
                <div className="col-xs-12 col-md-9">
                  <div className="row xs-margin-top sm-margin-top">
                    <div className="col-xs-12 col-sm-8 col-md-9">
                      <div className="form-group">
                        <input
                          className="form-control"
                          disabled={
                            this.props.search.isLoading || this.state.isLoading
                          }
                          onChange={this.onQueryChange}
                          type="text"
                          value={this.state.query}
                        />
                      </div>
                    </div>
                    <div className="col-xs-12 col-sm-4 col-md-3">
                      <button
                        className="btn btn-primary btn-block btn-outline"
                        disabled={
                          this.props.search.isLoading || this.state.isLoading
                        }
                      >
                        {gettext("Search")}
                      </button>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </form>
        </div>
      </div>
    )
  }
}
