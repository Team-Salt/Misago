import React from "react"
import Loader from "limitless/components/loader"

export default class extends React.Component {
  render() {
    return (
      <div className="modal-body modal-loader">
        <Loader />
      </div>
    )
  }
}
