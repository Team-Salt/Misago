import React from "react"
import Loader from "limitless/components/loader"

export default class extends React.Component {
  render() {
    return (
      <div className="panel-body panel-body-loading">
        <Loader className="loader loader-spaced" />
      </div>
    )
  }
}
