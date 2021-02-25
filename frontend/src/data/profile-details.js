import React from "react"
import { load } from "limitless/reducers/profile-details"
import ajax from "limitless/services/ajax"
import snackbar from "limitless/services/snackbar"

export default class extends React.Component {
  componentDidMount() {
    const { data, dispatch, user } = this.props
    if (data && data.id === user.id) return

    ajax.get(this.props.user.api.details).then(
      data => {
        dispatch(load(data))
      },
      rejection => {
        snackbar.apiError(rejection)
      }
    )
  }

  render() {
    return this.props.children
  }
}
