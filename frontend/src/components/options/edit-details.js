import React from "react"
import Form from "limitless/components/edit-details"
import title from "limitless/services/page-title"
import snackbar from "limitless/services/snackbar"

export default class extends React.Component {
  componentDidMount() {
    title.set({
      title: gettext("Edit details"),
      parent: gettext("Change your options")
    })
  }

  onSuccess = () => {
    snackbar.info(gettext("Your details have been updated."))
  }

  render() {
    return (
      <Form api={this.props.user.api.edit_details} onSuccess={this.onSuccess} />
    )
  }
}
