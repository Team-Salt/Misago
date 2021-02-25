import React from "react"
import Loader from "limitless/components/loader"

export default function({ display }) {
  if (!display) return null

  return (
    <div className="panel-body">
      <Loader />
    </div>
  )
}
